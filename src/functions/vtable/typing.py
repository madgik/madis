"""
.. function:: typing(query:None[,defaulttype[,column:type]])

    Returns the result of the input *query* casting types according to *column:type* pairs and cast rest of the columns to optional *defaulttype*.

:Returned table schema:
    Column names same as input query, types as defined in parameters.

Examples:

    >>> table1('''
    ... James   10	2
    ... Mark    7	3
    ... Lila    74	1
    ... ''')
    >>> sql("coltypes select * from table1")
    column | type
    -------------
    a      | str
    b      | str
    c      | str
    >>> sql("coltypes typing  a:text b:integer c:integer select * from table1")
    column | type
    ----------------
    a      | text
    b      | integer
    c      | integer
    >>> sql("coltypes typing 'integer' a:text select * from table1")
    column | type
    ----------------
    a      | text
    b      | integer
    c      | integer
    
"""
import setpath
from lib.sqlitetypes import typestoSqliteTypes
from vtiterable import SourceVT
from lib.iterutils import peekable
import functions



registered=True


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



class TypingCursor:
    def __init__(self,sqlquery,connection,first,names,types,*resttype,**destypes):
        if len(resttype)>1:
            raise functions.OperatorError(__name__.rsplit('.')[-1],"Cannot resolve more than one unbound types")
        
        self.sqlquery=sqlquery
        self.connection=connection
        self.c=self.connection.cursor()

        self.cols=names
        self.types=types
        if first:
            first = False
            try:
                execit=peekable(self.c.execute(self.sqlquery))
                samplerow=execit.peek()
                qnames=[str(v[0]) for v in self.c.getdescription()]
                if not resttype:
                    qtypes=[str(v[1]) for v in self.c.getdescription()]
                else:
                    qtypes=[resttype[0]]*len(qnames) ### fill types with resttype first element
                
                for el in destypes:
                    p=-1
                    try:
                        p=qnames.index(el)
                    except ValueError:
                        raise functions.OperatorError(__name__.rsplit('.')[-1],"Unknown column name '%s'" %(el))
                    qtypes[p]=destypes[el]
                for i in qnames:
                    self.cols.append(i)
                for i in qtypes:
                    self.types.append(i)
            except StopIteration:
                try:
                    raise
                finally:
                    try:
                        self.c.close()
                    except:
                        pass
                    
            self.iter=typed(self.types,execit)
        else:
            self.iter=typed(self.types,self.c.execute(self.sqlquery))
    def close(self):
        self.c.close()
    def next(self):
        return self.iter.next()
    def __iter__(self):
        return self

class TypingVT:
    def __init__(self,envdict,largs,dictargs): #DO NOT DO ANYTHING HEAVY
        self.largs=largs
        self.envdict=envdict
        self.dictargs=dictargs
        self.nonames=True
        self.names=[]
        self.types=[]
        if 'query' not in dictargs:
            raise functions.OperatorError(__name__.rsplit('.')[-1]," needs query argument ")
        self.query=dictargs['query']
        del dictargs['query']
    def getdescription(self):
        if not self.names:
            raise functions.OperatorError(__name__.rsplit('.')[-1],"VTable getdescription called before initiliazation")
        self.nonames=False
        return [(i,j) for i,j in zip(self.names,self.types)]
    def open(self):
        return TypingCursor(self.query,self.envdict['db'],self.nonames,self.names,self.types,*self.largs,**self.dictargs)
    def destroy(self):
        pass



def Source():
    return SourceVT(TypingVT)



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


