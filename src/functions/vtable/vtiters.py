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
from lib.iterutils import peekable


#'getschema':{'type':'STATIC','func':func}
#'getschema':{'type':'SAMPLE','func':func}
#'getschema':{'type':'DYNAMIC','func':func}

#SourceVT(parsefunction=default,iteratorfunc=xxx,getschemasettings=xxxx)


###staticSchema?????
class SimpleVT():
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


class SchemaFromSampleVT(SimpleVT):
    def getschema(self,samplerow):
        raise NotImplementedError

class StaticSchemaVT(SimpleVT):
    def getschema(self):
        raise NotImplementedError

class SchemaFromArgsVT(SimpleVT):
    def getschema(self,args):
        raise NotImplementedError



FuncTypes={
'static':1,
'dynamic':2,
'sample':3
}

def getTypeOfInstance(cls):
    try:
        if issubclass(cls, StaticSchemaVT):
            return FuncTypes['static']
        else:
            raise Exception
    except Exception:
        try:
            if issubclass(cls, SchemaFromArgsVT):
                return FuncTypes['dynamic']
            else:
                raise Exception
        except Exception:
            try:
                if issubclass(cls, SchemaFromSampleVT):
                    return FuncTypes['sample']
                else:
                    raise Exception
            except Exception:
                return None


# Decorator to extended a function by calling first another function with no arguments
def echocall(func):
    def wrapper(*args, **kw):
        obj=args[0]
        Extra=""
        if 'tablename' in obj.__dict__:
            Extra=obj.tablename
        if functions.settings['vtdebug']:
            print "Table %s:Before Calling %s.%s(%s)" %(Extra+str(obj),obj.__class__.__name__,func.__name__,','.join([repr(l) for l in args[1:]]+["%s=%s" %(k,repr(v)) for k,v in kw.items()]))
            aftermsg="Table %s:After Calling %s.%s(%s)" %(Extra,obj.__class__.__name__,func.__name__,','.join([repr(l) for l in args[1:]]+["%s=%s" %(k,repr(v)) for k,v in kw.items()]))
        a=func(*args, **kw)
        if functions.settings['vtdebug']:
            pass
        return a
    return wrapper


autostring='automatic_vtable:1'

class SourceCachefreeVT:
    def __init__(self,fobj): ####parse auto argument and throw!!!!
        self.tableObjs=dict()
        self.fobj=fobj
        self.typeOfObj=getTypeOfInstance(fobj)

    @echocall
    def Create(self, db, modulename, dbname, tablename,*args):
        global FuncTypes
        envars={'tablename':tablename,'db':db,'dbname':dbname,'modulename':modulename}
        auto=False
        iterator=None
        notuple=False
        uargs=[argsparse.unquote(a) for a in args]
        if len(uargs)>0 and uargs[-1]==autostring:
            auto=True
            uargs=uargs[:-1]
        TableVT=self.fobj()
        parsedArgs = list(TableVT.parse(*uargs))
        openIterFunc=None

        if self.typeOfObj==FuncTypes['static']:
            schema = TableVT.getschema()
            openIterFunc= lambda:TableVT.open(*parsedArgs,**envars)
        elif self.typeOfObj==FuncTypes['dynamic']:
            try:
                schema = TableVT.getschema(*parsedArgs,**envars)
                openIterFunc= lambda:TableVT.open(*parsedArgs,**envars)
            except (StopIteration,apsw.ExecutionCompleteError),e: ###
                raise functions.DynamicSchemaWithEmptyResultError(envars['modulename'])
        elif self.typeOfObj==FuncTypes['sample']:
            notuple=True
            iterator = peekable(TableVT.open(*parsedArgs,**envars))
            try:
                samplerow = iterator.peek()
                schema = TableVT.getschema(samplerow)
                openIterFunc= lambda:TableVT.open(*parsedArgs,**envars)
            except (StopIteration,apsw.ExecutionCompleteError),e:
                try:
                    raise functions.DynamicSchemaWithEmptyResultError(envars['modulename'])
                finally:
                    try:
                        if hasattr(iterator,'close'):
                            iterator.close()
                    except:
                        pass
        else:
            raise functions.MadisError(envars['modulename'])
        if auto and iterator!=None:
            if functions.settings['vtdebug']:
                print "Manual vtable creation:Closing Vtable iterator"
            if hasattr(iterator,'close'):
                iterator.close()
            iterator=None

        self.tableObjs[tablename]=(schemaUtils.CreateStatement(schema,tablename),LTable(self.tableObjs,envars,TableVT,openIterFunc,ommituple=notuple,openedIter=iterator))
        if functions.settings['tracing']:
            print 'VT_Schema: %s' %(self.tableObjs[tablename][0])
        return self.tableObjs[tablename]
    @echocall
    def Connect(self, db, modulename, dbname, tablename,*args):
        if tablename not in self.tableObjs:
            return self.Create( db, modulename, dbname, tablename,*args)
        return self.tableObjs[tablename]

import sys

class emptyiter:
    def init(self):
        pass
    def __iter__(self):
        return self
    def next(self):
        raise StopIteration
    def close(self):
        pass

class LTable: ####Init means setschema and execstatus
    
    @echocall
    def __init__(self, tblist, envars,tableObj , iterFunc, ommituple = False ,openedIter=None): # tablename, auto , cursorfunc, ommit tuple OPTIONAL []

        self.tblist=tblist
        self.envars=envars
        self.iterFunc=iterFunc
        self.openedIter=openedIter
        self.tableObj=tableObj
        self.ommituple=ommituple


    @echocall
    def BestIndex(self, *args):
        return None
    @echocall
    def Open(self):
        return Cursor(self.iterFunc, self.openedIter, self.envars , self.ommituple)

    @echocall
    def Disconnect(self):
        """
        This method is called when a reference to a virtual table is no longer used
        """
        if self.tableObj.__class__.__dict__.has_key('disconnect'):
            self.tableObj.disconnect()
    @echocall
    def Destroy(self):
        """
        This method is called when the table is no longer used
        """
        del self.tblist[self.envars['tablename']]
        if self.tableObj.__class__.__dict__.has_key('destroy'):
            self.tableObj.destroy()



# Represents a cursor
class Cursor: ##### Needs Cursor Function , Iterator instance, tablename ...... if has close

    @echocall
    def __init__(self, openFunc,openIter,envars,ommituple):
        if ommituple:
            self.Next=self.NextNonTuple
        else:
            self.Next=self.NextAny
        self.envars=envars
        self.openFunc=openFunc
        if openIter!=None:
            self.iter=openIter
        else:
            self.iter=openFunc()
        self.row=None
        self.firsttime=True



    @echocall
    def Filter(self, *args):
        self.eof=False
        self.pos=-1

        if not self.firsttime:
            if hasattr(self.iter,'close'):
                self.iter.close()
            self.iter=self.openFunc()
        self.firsttime=False
        self.Next()

    @echocall
    def Eof(self):
        return self.eof
    @echocall
    def Rowid(self):
        return self.pos+1
    @echocall
    def Column(self, col):
        try:
            return self.row[col]
        except IndexError:
            raise functions.OperatorError(self.envars['modulename'] ,"Not enough data in rowid: %s" %(self.pos+1))
    @echocall
    def NextNonTuple(self):
        while True:
            try:
                self.row=self.iter.next()
                if 'tuple' not in str(type(self.row)):
                    self.pos+=1
                    break
            except StopIteration:
                self.row=None
                self.eof=True
                break
    def NextAny(self):
        try:
            self.row=self.iter.next()
            self.pos+=1
        except StopIteration:
            self.row=None
            self.eof=True
    @echocall
    def Close(self):
        if hasattr(self.iter,'close'):
            self.iter.close()        

