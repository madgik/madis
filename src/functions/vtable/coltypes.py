"""
.. function:: coltypes(query:None)

Returns the input query results column names and types.

:Returned table schema:
    - *column* text
        Column name of input query *schema*
    - *type* text
        Type of column

Examples:

    >>> sql("coltypes select 5 as vt")
    column | type
    -------------
    vt     | None

Applying coltypes in the result of virtual table func:`typing` function in the same query

    >>> sql("coltypes typing 'vt:int' select 5 as vt")
    column | type
    -------------
    vt     | int

.. doctest::
    :hide:

    >>> sql("select * from (coltypes typing 'text' select '10' ) as a, (coltypes typing 'int' select '10' ) as b where a.column=b.column")
    column | type | column | type
    -----------------------------
    '10'   | text | '10'   | int
"""

import setpath
from vtiterable import SourceVT
import functions

registered=True


class TypesCursor:
    def __init__(self,sqlquery,connection,first,results,*resttype,**destypes):
        if len(resttype)>1:            
            raise functions.OperatorError(__name__.rsplit('.')[-1],"Cannot resolve more than one unbound types")

        self.sqlquery=sqlquery
        self.connection=connection
        if first:
            try:
                self.c=self.connection.cursor()
                execit=self.c.execute(self.sqlquery)
                samplerow=execit.next()
                vals=self.c.getdescription()
                self.vals=vals
                for i in vals:
                    results.append(i)
            except StopIteration:
                try:
                    raise
                finally:
                    try:
                        self.c.close()
                    except:
                        pass
        self.iter=iter(results)

        
    def close(self):
        pass
    def next(self):
        return self.iter.next()
    def __iter__(self):
        return self

class TypesVT:
    def __init__(self,envdict,largs,dictargs): #DO NOT DO ANYTHING HEAVY
        self.largs=largs
        self.envdict=envdict
        self.dictargs=dictargs
        self.nonames=True
        self.names=["column","type"]
        self.result=[]
        if 'query' not in dictargs:
            raise functions.OperatorError(__name__.rsplit('.')[-1]," needs query argument ")
        self.query=dictargs['query']
        del dictargs['query']
    def getdescription(self):
        if not self.names:
            raise functions.OperatorError(__name__.rsplit('.')[-1],"VTable getdescription called before initiliazation")
        return [(i,) for i in self.names]
    def open(self):
        if self.result!=[]:
            self.nonames=False
        return TypesCursor(self.query,self.envdict['db'],self.nonames,self.result,*self.largs,**self.dictargs)
    def destroy(self):
        pass



def Source():
    return SourceVT(TypesVT,staticschema=True)




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