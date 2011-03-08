"""
.. function:: flow(query:None)

Translates the input query results into sql statements if possible.

:Returned table schema:
    - *query* text
        A complete sql query statement with the semicolon at the end

.. note::

    Input query results must be sql statements separated with semicolons in the first place. Using in the input query the :func:`~functions.vtable.file.file` operator any file with sql statements can be divided in sql query statements. Multiline comments are considered as statements.



Examples:

.. doctest::
    
    >>> sql("select * from (flow file 'testing/testflow.sql') limit 1") # doctest: +NORMALIZE_WHITESPACE
    query
    -----------------------------------------------------------------------------------------------------------------------------------------------------------
    /*====== countries: table of Country ISO codes , country names ===========*/
    CREATE TABLE countries (
        country2 PRIMARY KEY UNIQUE,
        country_name
    );
    >>> sql("select * from (flow file 'testing/colpref.csv' limit 5) ")
    Traceback (most recent call last):
    ...
    OperatorError: Madis SQLError: operator flow: Incompete statement found : userid colid pr ... 41 416900.0 agr


Test files:

- :download:`testflow.sql <../../functions/vtable/testing/testflow.sql>`
- :download:`colpref.csv <../../functions/vtable/testing/colpref.csv>`



"""
import setpath
from lib.sqlitetypes import typestoSqliteTypes
from vtiterable import SourceVT
from lib.iterutils import peekable
import functions
import apsw


registered=True


def sqlstatement(iter):
    st=''
    for row in iter:
        strow=' '.join(row)
        if strow=='':
            continue
        if st!='':
            st+='\n'+strow
        else:
            st+=strow
        if apsw.complete(st):
            yield [st]
            st=''
    if len(st)>0:
        if len(st)>35:
            raise functions.OperatorError(__name__.rsplit('.')[-1],"Incompete statement found : %s ... %s" %(st[:15],st[-15:]))
        else:
            raise functions.OperatorError(__name__.rsplit('.')[-1],"Incompete statement found : %s" %(st))
    return



class PlanCursor:
    def __init__(self,sqlquery,connection):
        self.sqlquery=sqlquery
        self.connection=connection
        self.c=self.connection.cursor()
        self.iter=sqlstatement(self.c.execute(self.sqlquery))
    def close(self):
        self.c.close()
    def next(self):
        return self.iter.next()
    def __iter__(self):
        return self

class PlanVT:
    def __init__(self,envdict,largs,dictargs): #DO NOT DO ANYTHING HEAVY
        self.largs=largs
        self.envdict=envdict
        self.dictargs=dictargs
        self.nonames=True
        self.names=['query']
        self.types=[]
        if 'query' not in dictargs:
            raise functions.OperatorError(__name__.rsplit('.')[-1],"needs query argument ")
        self.query=dictargs['query']
        del dictargs['query']
    def getdescription(self):
        return [(i,) for i in self.names]

    def open(self):
        return PlanCursor(self.query,self.envdict['db'])
    def destroy(self):
        pass



def Source():
    return SourceVT(PlanVT,staticschema=True)



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


