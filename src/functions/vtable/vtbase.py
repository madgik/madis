"""
Basis code for Virtual table, without cache.

Static schema Virtual table:
    subclass StaticSchemaVT

Dynamic schema Virtual table. The schema is extracted from a samplerow:
    subclass SchemaFromSampleVT

    **Note: to ommit header info from being returned to the system but to be in the sample row,
    if the iterator returns a tuple it is ignored and not promoted to sqlite. The first row usually independent of the type will be given to getschema function

"""

import setpath
import functions
import apsw
from lib import argsparse ,schemaUtils

autostring='automatic_vtable:1'

# Decorator to extended a function by calling first another function with no arguments
def echocall(func):
    def wrapper(*args, **kw):
        if functions.settings['vtdebug']:
            obj=args[0]
            Extra=""
            if 'tablename' in obj.__dict__:
                Extra=obj.tablename
            print "Table %s:Before Calling %s.%s(%s)" %(Extra+str(obj),obj.__class__.__name__,func.__name__,','.join([repr(l) for l in args[1:]]+["%s=%s" %(k,repr(v)) for k,v in kw.items()]))
        return func(*args, **kw)
    return wrapper

class VT():
    def parse(self,*args):
        return args
    def full_parse(self,args,boolargs=None,nonstringargs=None,needsescape=None, notsplit=None):
        return argsparse.parse(args,boolargs,nonstringargs,needsescape,notsplit)
    def open(self,*args,**kargs):
        raise NotImplementedError
    def disconnect(self):
        pass
    def destroy(self):
        pass

class VTGenerator:
    def __init__(self,fobj): ####parse auto argument and throw!!!!
        self.tableObjs=dict()
        self.fobj=fobj

    @echocall
    def Create(self, db, modulename, dbname, tablename,*args):
        envars={'tablename':tablename,'db':db,'dbname':dbname,'modulename':modulename}
        uargs=[argsparse.unquote(a) for a in args]
        if len(uargs)>0 and uargs[-1]==autostring:
            auto=True
            uargs=uargs[:-1]
        TableVT=self.fobj()
        parsedArgs = list(TableVT.parse(*uargs))
        iterFunc = lambda:TableVT.VTiter(*parsedArgs,**envars)
        openedIter = iterFunc()
        try:
            schema = openedIter.next()
        except (StopIteration,apsw.ExecutionCompleteError),e:
            try:
                if hasattr(openedIter,'close'):
                    openedIter.close()
            except:
                pass
            raise functions.DynamicSchemaWithEmptyResultError(envars['modulename'])

        self.tableObjs[tablename]=(schemaUtils.CreateStatement(schema,tablename),LTable(self.tableObjs, envars, TableVT, iterFunc, openedIter))
        if functions.settings['tracing']:
            print 'VT_Schema: %s' %(self.tableObjs[tablename][0])
        return self.tableObjs[tablename]
    @echocall
    def Connect(self, db, modulename, dbname, tablename,*args):
        if tablename not in self.tableObjs:
            return self.Create( db, modulename, dbname, tablename,*args)
        return self.tableObjs[tablename]

class LTable: ####Init means setschema and execstatus
    @echocall
    def __init__(self, tblist, envars, tableObj , iterFunc ,openedIter=None): # tablename, auto , cursorfunc, ommit tuple OPTIONAL []
        self.tblist=tblist
        self.envars=envars
        self.iterFunc=iterFunc
        self.openedIter=openedIter
        self.tableObj=tableObj
        self.cursors = []
        try:
            self.BestIndex = tableObj.BestIndex
        except AttributeError:
            self.BestIndex = self.defaultBestIndex

    @echocall
    def defaultBestIndex(self, *args):
        return (None, 0, None, False, 1000)

    @echocall
    def Open(self):
        tmpIter = None
        if self.openedIter == None:
            tmpIter = self.iterFunc()
            tmpIter.next()
        else:
            tmpIter = self.openedIter
            self.openedIter = None

        c = Cursor(self.iterFunc, tmpIter, self.envars)
        self.cursors.append(c)
        return c

    def CloseCursors(self):
        for c in self.cursors:
            c.Close()
        self.cursors = []

    @echocall
    def Disconnect(self):
        """
        This method is called when a reference to a virtual table is no longer used
        """
        self.CloseCursors()
        if self.tableObj.__class__.__dict__.has_key('disconnect'):
            self.tableObj.disconnect()

    @echocall
    def Destroy(self):
        """
        This method is called when the table is no longer used
        """
        self.CloseCursors()
        del self.tblist[self.envars['tablename']]
        if self.tableObj.__class__.__dict__.has_key('destroy'):
            self.tableObj.destroy()

# Represents a cursor
class Cursor: ##### Needs Cursor Function , Iterator instance, tablename ...... if has close
    @echocall
    def __init__(self, iterFunc, openIter,envars):
        self.envars=envars
        self.firsttime = True
        self.openIter=openIter
        self.iterFunc=iterFunc
        self.row = []
        self.eof = False
        self.pos=0

    @echocall
    def Filter(self, *args):
        self.eof=False
        self.pos=0

        if not self.firsttime or self.openIter == None:
            if hasattr(self.openIter,'close'):
                self.openIter.close()
            self.openIter=self.iterFunc()
            self.openIter.next()
        self.firsttime=False

        self.Next()
        return
    
    @echocall #-- Commented out for speed reasons
    def Eof(self):
        return self.eof

    @echocall
    def Rowid(self):
        return self.pos

    @echocall #-- Commented out for speed reasons
    def Column(self, col):
        try:
            return self.row[col]
        except IndexError:
            raise functions.OperatorError(self.envars['modulename'] ,"Not enough data in rowid: %s" %(self.pos+1))

    @echocall #-- Commented out for speed reasons
    def Next(self):
        try:
            self.row=self.openIter.next()
            self.pos+=1
        except StopIteration:
            self.row=[]
            self.eof=True
            self.Close()

    @echocall
    def Close(self):
        if hasattr(self.openIter, 'close'):
            self.openIter.close()
        self.openIter = None

