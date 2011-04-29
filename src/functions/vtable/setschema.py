"""

.. function:: setschema(query:None,schemadefinition)

    Returns the result of the input *query* with changed schema according to *schemadefinition* parameter.
    Parameter *schemadefinition* is text identical to schema definition between parenthesis of a CREATE TABLE SQL statement.
    
    Can perform renaming, typecasting and projection on some columns of the input *query* result.

.. note::

    This function can be used to avoid DynamicSchemaWithEmptyResultError caused by dynamic schema virtual tables on empty query input result.

    .. toadd link.
    
    

:Returned table schema:
    As defined at *schemadefinition* parameter.


Examples::

    >>> sql("setschema 'col1 int,col2 text' select 5,6")
    col1 | col2
    -----------
    5    | 6
    >>> sql("select strplitv(q) from (select 5 as q) where q!=5")
    Traceback (most recent call last):
    ...
    SQLError: SQLError: no such function: strplitv
    >>> sql("setschema 'a,b' (select strsplitv(q) from (select 5 as q) where q!=5)")

    >>> sql("select * from (file file:testing/colpref.csv dialect:csv header:t) limit 3")
    userid | colid | preference | usertype
    --------------------------------------
    agr    |       | 6617580.0  | agr
    agr    | a0037 | 2659050.0  | agr
    agr    | a0086 | 634130.0   | agr

The query below has constraints preference column to be less than an int value , but preference is text ( outcomes from :func:`~functions.vtable.file.file` are *text*), so an empty result is produced
    
    >>> sql("select * from (select * from (file file:testing/colpref.csv dialect:csv header:t) limit 3) where preference<634131")

With setschema functions preference column is casted as float.
    
    >>> sql("select * from (setschema 'type,colid , pref float, userid' select * from (file file:testing/colpref.csv dialect:csv header:t) limit 3) where pref<634131")
    type | colid | pref     | userid
    --------------------------------
    agr  | a0086 | 634130.0 | agr

"""
import StringIO
import setpath
from lib.sqlitetypes import typestoSqliteTypes
from vtiterable import SourceVT
from lib.iterutils import peekable
import functions
import apsw
from lib.dsv import reader
from lib.pyparsing import Word, alphas, alphanums, Optional, Group, delimitedList, quotedString , ParseBaseException


registered=True


ident = Word(alphas+"_",alphanums+"_")
columnname = ident | quotedString
columndecl = Group(columnname + Optional(ident))
listItem = columndecl

def parsesplit(s):
    global listItem
    return delimitedList(listItem).parseString(s,parseAll=True).asList()



def typed(types,iter):
    sqlitecoltype=[typestoSqliteTypes(type) for type in types]
    for el in iter:
        ret =[]
        for col,type in zip(el,sqlitecoltype):
            e=col
            if type=="INTEGER" or type=="REAL" or type=="NUMERIC":
                try:
                    e=int(col)
                except ValueError:
                    try:
                        e=float(col)
                    except ValueError:
                        e=col
            ret+=[e]
        yield ret

def checkexceptionisfromempty(e):
    e=str(e).lower()
    if 'no' in e and 'such' in e and 'table' in e and 'vt_' in e:
        return True
    return False

class SetschemaCursor:
    def __init__(self,sqlquery,connection,first,names,types,*largs,**kargs):
        """
        Works only with one argument splited with ,,,,
        """
        if first:
            if len(largs)<1:
                raise functions.OperatorError(__name__.rsplit('.')[-1]," Schema argument was not provided")
            try:
                schema=parsesplit(largs[0])
            except ParseBaseException:
                raise functions.OperatorError(__name__.rsplit('.')[-1]," Error in schema definition: %s" %(largs[0]))
            for el in schema:
                names.append(el[0])
                if len(el)>1:
                    types.append(el[1])
                else:
                    types.append('None')

        self.c=connection.cursor()
        self.openedc=True
        try:

            if first:
                ### Find names and types
                execit=peekable(self.c.execute(sqlquery))
                samplerow=execit.peek()
                qtypes=[str(v[1]) for v in self.c.getdescription()]
                if len(qtypes)<len(types):
                    raise functions.OperatorError(__name__.rsplit('.')[-1],"Setting more columns than result query")

                for i in xrange(len(types)):
                    if types[i]=="None" and qtypes[i]!="None":
                        types[i]=qtypes[i]
                self.iter=typed(types,execit)
            else:
                self.iter=typed(types,self.c.execute(sqlquery))
        except StopIteration: ### if exception keep schema
            try:
                self.iter=iter([])
                self.openedc=False
            finally:
                try:
                    self.c.close()
                except:
                    pass
        except apsw.SQLError, e: ### if exception SQLERROR check if it is from empty schema
            try:
                if not checkexceptionisfromempty(e):
                    raise
                else:
                    self.iter=iter([])
                    self.openedc=False
            finally:
                try:
                    self.c.close()
                except:
                    pass

    def close(self):
        if self.openedc:
            self.c.close()
    def next(self):
        return self.iter.next()
    def __iter__(self):
        return self

class SetschemaVT:
    def __init__(self,envdict,largs,dictargs): #DO NOT DO ANYTHING HEAVY
        self.largs=largs
        self.envdict=envdict
        self.dictargs=dictargs
        self.nonames=True
        self.names=[]
        self.types=[]
        if 'query' not in dictargs:
            raise functions.OperatorError(__name__.rsplit('.')[-1],"No query argument ")
        self.query=dictargs['query']
        del dictargs['query']
    def getdescription(self):
        if not self.names:
            raise functions.OperatorError(__name__.rsplit('.')[-1],"VTable getdescription called before initiliazation")
        self.nonames=False
        return [(i,j) for i,j in zip(self.names,self.types)]
    def open(self):
        return SetschemaCursor(self.query,self.envdict['db'],self.nonames,self.names,self.types,*self.largs,**self.dictargs)
    def destroy(self):
        pass



def Source():
    return SourceVT(SetschemaVT)



if not ('.' in __name__):
    """
    This is needed to be able to test the function, put it at the end of every
    new function you create
    """
    import sys
    import setpath
    from functions import *
    testfunction()
    if __name__ == "__main__":
        reload(sys)
        sys.setdefaultencoding('utf-8')
        import doctest
        doctest.testmod()



