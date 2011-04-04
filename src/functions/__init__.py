"""functions
"""
import os.path
import os
import apsw
import setpath
import sqltransform
import traceback
import logging
import re
import sys
from lib import simplequeryparse


firstimport=True
test_connection = None

settings={
'tracing':False,
'vtdebug':False,
'logging':False,
'beep':False,
'syspath':str(os.path.abspath(os.path.expandvars(os.path.expanduser(os.path.normcase(sys.path[0])))))
}

functions = {'row':{},'aggregate':{}, 'vtable':{}}
multiset_functions = {}

variables=lambda x:x
variables.flowname=''
variables.execdb=None

privatevars=lambda x:x

rowfuncs=lambda x:x

oldexecdb=-1

def mstr(s):
    strs=''
    unis=''
    try:
        strs=str(s)
    except:
        pass
    try:
        unis=unicode(s)
    except:
        pass
    fs=''
    if unis=='' and strs!='':
        fs=strs
    else:
        fs=unis
    o=repr(fs)
    if (o[0:2]=="u'" and o[-1]=="'") or (o[0:2]=='u"' and o[-1]=='"'):
        o=o[2:-1]
    elif (o[0]=="'" and o[-1]=="'") or (o[0]=='"' and o[-1]=='"'):
        o=o[1:-1]
    o=o.replace('''\\n''','\n')
    return o

class MadisError(Exception):
    def __init__(self,msg):
        self.msg=mstr(msg)
    def __str__(self):
        merrormsg="Madis SQLError: \n"
        if self.msg.startswith(merrormsg):
            return self.msg
        else:
            return merrormsg+self.msg

class OperatorError(MadisError):
    def __init__(self,opname,msg):
        self.msg="Operator %s: %s" %(mstr(opname.upper()),mstr(msg))

class DynamicSchemaWithEmptyResultError(MadisError):
    def __init__(self,opname):
        self.msg="operator %s: Cannot initialise dynamic schema virtual table without data" %(str(opname))

def echofunctionmember(func):
    def wrapper(*args, **kw):
        if settings['tracing']:
            if settings['logging']:
                try:
                    lg = logging.LoggerAdapter(logging.getLogger(__name__),{ "flowname" : variables.flowname  })
                    if hasattr(lg.logger.parent.handlers[0],'baseFilename'):
                        lg.info("%s(%s)" %(func.__name__,','.join(list([repr(el) for el in args[1:]])+["%s=%s" %(k,repr(v)) for k,v in kw.items()])))
                except Exception:
                    pass
            print "%s(%s)" %(func.__name__,','.join(list([repr(el)[:200]+('' if len(repr(el))<=200 else '...') for el in args[1:]])+["%s=%s" %(k,repr(v)) for k,v in kw.items()]))
        return func(*args, **kw)
    return wrapper

def checkhassetschema(vts,vt):
    vtname=vt[0].lower()
    qis="'query:SELECT * FROM %s" %(vt[0])
    qis=qis.lower()
    for i in vts:
        vtparam=i[2].lower()
        vtsoperator=i[1].lower()
        if vtname in vtparam:
            if vtsoperator!='setschema':
                return False
            relatedtbs=simplequeryparse.dependencytbs(vtparam)
            if not relatedtbs or len(relatedtbs)>1 or relatedtbs[0]!=vtname:
                return False
    return True

class Cursor(object):
    def __init__(self,w):
        self.__wrapped=w
        self.__vtables=[]
        self.__initialised=True
        
    def __getattr__(self, attr):
        if self.__dict__.has_key(attr):
            return self.__dict__[attr]
        return getattr(self.__wrapped, attr)
    def __setattr__(self, attr, value):
        if self.__dict__.has_key(attr):
            return dict.__setattr__(self, attr, value)
        if not self.__dict__.has_key('_Cursor__initialised'):  # this test allows attributes to be set in the __init__ method
            return dict.__setattr__(self, attr, value)
        return setattr(self.__wrapped, attr, value)
    @echofunctionmember
    def executetrace(self,statements,bindings=None):
        return self.__wrapped.execute(statements,bindings)
    def execute(self,statements,bindings=None,parse=True): #overload execute statement
        if bindings==None:
            bindings=variables.__dict__
        else:
            bindings.update(variables.__dict__)

        if not parse:            
            return self.executetrace(statements,bindings)
        svts=sqltransform.transform(statements, multiset_functions.keys(), functions['vtable'], functions['row'].keys(), substitute=functions['row']['subst'])
        s=svts[0]
        try:
            if self.__vtables!=[]:
                self.executetrace(''.join(['drop table ' + 'temp.'+x +';' for x in reversed(self.__vtables)]))
                self.__vtables=[]
            for i in svts[1]:
                if re.match(r'\s*$',i[2])==None:
                    sep=','
                else:
                    sep=''
                try:
                    self.executetrace('create virtual table ' + 'temp.'+i[0]+ ' using ' + i[1] + "(" + i[2] + sep + "'automatic_vtable:1'" +")")
                    self.__vtables.append(i[0])
                except DynamicSchemaWithEmptyResultError:                    
                    if not checkhassetschema(svts[1],i) or i[0] in s:
                        raise
            return self.executetrace(s,bindings)
        except Exception:
            if settings['tracing']:
                print traceback.print_exc()
            try: #avoid masking exception in recover statements
                raise
            finally:
                try:
                    if self.__vtables!=[]:
                        self.executetrace(''.join(['drop table ' + 'temp.'+x +';' for x in reversed(self.__vtables)]))
                        self.__vtables=[]
                except:
                    pass

    def getdescription(self):
        return self.__wrapped.getdescription()
    def close(self, force=False):
        if self.__vtables!=[]:
            self.executetrace(''.join(['drop table ' + 'temp.'+x +';' for x in reversed(self.__vtables)]))
            self.__vtables=[]
        return self.__wrapped.close(force)

class Connection(apsw.Connection):
    def cursor(self):
        return Cursor(apsw.Connection.cursor(self))
    @echofunctionmember
    def close(self):
        apsw.Connection.close(self)

def register(connection=None):
    global firstimport, oldexecdb

    functionspath=os.path.abspath(__path__[0])

    if connection==None:
        connection=Connection(':memory:')

    connection.cursor().execute("attach database ':memory:' as mem;",parse=False)

    def findmodules(abspath, relativepath):
        return [ os.path.splitext(file)[0] for file
                in os.listdir(os.path.join(abspath , relativepath))
                if file.endswith(".py") and not file.startswith("_") ]

    rowfiles = findmodules(functionspath, 'row')
    aggrfiles = findmodules(functionspath, 'aggregate')
    vtabfiles = findmodules(functionspath, 'vtable')

    [__import__("functions.row" + "." + module) for module in rowfiles]
    [__import__("functions.aggregate" + "." + module) for module in aggrfiles]
    [__import__("functions.vtable" + "." + module) for module in vtabfiles]

    # Register aggregate functions
    for module in aggrfiles:
        moddict = aggregate.__dict__[module]
        register_ops(moddict,connection)

    # Register row functions
    for module in rowfiles:
        moddict = row.__dict__[module]
        register_ops(moddict,connection)

    register_ops(vtable,connection)

    # Register madis local functions
    functionslocalpath=os.path.abspath(os.path.join(functionspath,'..','functionslocal'))

    flrowfiles = findmodules(functionslocalpath, 'row')
    flaggrfiles = findmodules(functionslocalpath, 'aggregate')
    flvtabfiles = findmodules(functionslocalpath, 'vtable')

    for module in flrowfiles:
        tmp=__import__("functionslocal.row" + "." + module)
        register_ops(tmp.row.__dict__[module], connection)

    for module in flaggrfiles:
        tmp=__import__("functionslocal.aggregate" + "." + module)
        register_ops(tmp.aggregate.__dict__[module], connection)

    localvtable=lambda x:x
    for module in flvtabfiles:
        localvtable.__dict__[module]=__import__("functionslocal.vtable" + "." + module)

    if len(flvtabfiles)!=0:
        register_ops(localvtable.vtable,connection)

    # Register db local functions
    if variables.execdb!=oldexecdb:
        oldexecdb=variables.execdb
        dbpath=None
        
        if variables.execdb!=None:
            dbpath=os.path.join(os.path.abspath(os.path.dirname(variables.execdb)),'functions')

        if dbpath==None or not os.path.exists(dbpath):
            currentpath=os.path.abspath(os.path.join(os.path.abspath('.'), 'functions'))
            if os.path.exists(currentpath):
                dbpath=currentpath

        if dbpath!=None and os.path.exists(dbpath):
            if os.path.abspath(dbpath)!=os.path.abspath(functionspath):

                sys.path.append(dbpath)

                if os.path.exists(os.path.join(dbpath, 'row')):
                    lrowfiles = findmodules(dbpath, 'row')
                    sys.path.append((os.path.abspath(os.path.join(os.path.join(dbpath),'row'))))
                    for module in lrowfiles:
                        tmp=__import__(module)
                        register_ops(tmp, connection)

                if os.path.exists(os.path.join(dbpath, 'aggregate')):
                    sys.path.append((os.path.abspath(os.path.join(os.path.join(dbpath),'aggregate'))))
                    laggrfiles = findmodules(dbpath, 'aggregate')
                    for module in laggrfiles:
                        tmp=__import__(module)
                        register_ops(tmp, connection)

                if os.path.exists(os.path.join(dbpath, 'vtable')):
                    sys.path.append((os.path.abspath(os.path.join(os.path.join(dbpath),'vtable'))))
                    lvtabfiles = findmodules(dbpath, 'vtable')
                    tmp=lambda x:x
                    for module in lvtabfiles:
                        tmp.__dict__[module]=__import__(module)

                    if localvtable!=None:
                        register_ops(tmp,connection)

    firstimport=False

def register_ops(module, connection):
    global rowfuncs, firstimport

    def opexists(op):
        if firstimport:
            return op in functions['vtable'] or op in functions['row'] or op in functions['aggregate']
        else:
            return False

    for f in module.__dict__:
        fobject = module.__dict__[f]
        if hasattr(fobject, 'registered') and type(fobject.registered).__name__ == 'bool' and fobject.registered == True:
            opname=f.lower()

            if firstimport:
                if opname!=f:
                    raise MadisError("Extended SQLERROR: Function '"+module.__name__+'.'+f+"' uses uppercase characters. Functions should be lowercase")

                if opname.upper() in sqltransform.sqlparse.keywords.KEYWORDS:
                    raise MadisError("Extended SQLERROR: Function '"+module.__name__+'.'+opname+"' is a reserved SQL function")

            if type(fobject).__name__ == 'module':
                if opexists(opname):
                    raise MadisError("Extended SQLERROR: Vtable '"+opname+"' name collision with other operator")
                functions['vtable'][opname] = fobject
                connection.createmodule(opname, fobject.Source())

            if type(fobject).__name__ == 'function':
                if opexists(opname):
                    raise MadisError("Extended SQLERROR: Row operator '"+module.__name__+'.'+opname+"' name collision with other operator")
                functions['row'][opname] = fobject
                setattr(rowfuncs, opname, fobject)
                connection.createscalarfunction(opname, fobject)

            if type(fobject).__name__ == 'classobj':
                if opexists(opname):
                    raise MadisError("Extended SQLERROR: Aggregate operator '"+module.__name__+'.'+opname+"' name collision with other operator")
                functions['aggregate'][opname] = fobject
                setattr(fobject,'factory',classmethod(lambda cls:(cls(), cls.step, cls.final)))
                connection.createaggregatefunction(opname, fobject.factory)

            if hasattr(fobject, 'multiset') and type(fobject.multiset).__name__ == 'bool' and fobject.multiset == True:
                    multiset_functions[opname]=True

def testfunction():
    global test_connection, settings

    test_connection = Connection(':memory:')
    register(test_connection)
    variables.execdb=':memory:'

def settestdb(testdb):
    import os

    global test_connection, settings

    abstestdb=str(os.path.abspath(os.path.expandvars(os.path.expanduser(os.path.normcase(testdb)))))
    test_connection = Connection(abstestdb)
    register(test_connection)
    variables.execdb=abstestdb

def sql(sqlquery):
    import locale
    from lib import pptable
    global test_connection
    
    language, output_encoding = locale.getdefaultlocale()

    if output_encoding==None:
        output_encoding="UTF8"

    test_cursor=test_connection.cursor()
        
    e=test_cursor.execute(sqlquery.decode(output_encoding))
    try:
        desc=test_cursor.getdescription()
        print pptable.indent([[x[0] for x in desc]]+[x for x in e], hasHeader=True),
    except apsw.ExecutionCompleteError:
        print '',
    test_cursor.close()

def table(tab, num=''):
    import shlex
    """
    Creates a test table named "table". It's columns are fitted to the data
    given to it and are automatically named a, b, c, ...

    'num' parameter:
    If a 'num' parameter is given then the table will be named for example
    table1 when num=1, table2 when num=2 ...

    Example:

    table('''
    1   2   3
    4   5   6
    ''')

    will create a table named 'table' having the following data:

    a   b   c
    ---------
    1   2   3
    4   5   6

    """
    
    colnames="abcdefghijklmnop"
    import re
    tab=tab.splitlines()
    tab=[re.sub(r'[\s\t]+',' ',x.strip()) for x in tab]
    tab=[x for x in tab if x!='']
    # Convert NULL to None
    tab=[[(y if y!='NULL' else None) for y in shlex.split(x)] for x in tab]

    numberofcols=len(tab[0])

    if num=='':
        num='0'

    createsql='create table table'+str(num)+'('
    insertsql="insert into table"+str(num)+" values("
    for i in range(0,numberofcols):
        createsql=createsql+colnames[i]+' str'+','
        insertsql=insertsql+'?,'

    createsql=createsql[0:-1]+')'
    insertsql=insertsql[0:-1]+')'

    test_cursor=test_connection.cursor()
    try:
        test_cursor.execute(createsql)
    except:
        test_cursor.execute("drop table table"+str(num))
        test_cursor.execute(createsql)

    test_cursor.executemany(insertsql, tab)

def table1(tab):
    table(tab, num=1)

def table2(tab):
    table(tab, num=2)

def table3(tab):
    table(tab, num=3)

def table4(tab):
    table(tab, num=4)

def table5(tab):
    table(tab, num=5)

def table6(tab):
    table(tab, num=6)

def setlogfile(file):
    pass
