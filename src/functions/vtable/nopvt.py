"""

.. function:: nopvt(query) -> query results

Returns the query input results without any change. NOPVT can be as a
barrier for SQLite's optimizer, for debugging etc.

:Returned table schema:
    Same as input query schema.

Examples::

    >>> table1('''
    ... James   10	2
    ... Mark    7	3
    ... Lila    74	1
    ... ''')
    >>> sql("nopvt select * from table1")
    a     | b  | c
    --------------
    James | 10 | 2
    Mark  | 7  | 3
    Lila  | 74 | 1
    
    >>> sql("nopvt select * from table1 order by c")
    a     | b  | c
    --------------
    Lila  | 74 | 1
    James | 10 | 2
    Mark  | 7  | 3

    Note the difference with rowid table column.

"""
import setpath
from vtiterable import SourceVT
import functions

### Classic stream iterator
registered=True
       
class NopCursor:
    def __init__(self, sqlquery, connection, schema):
        self.sqlquery=sqlquery
        self.connection=connection
        self.c=self.connection.cursor()

        self.iter = iter(self.c.execute(self.sqlquery))
        if schema==[]:
            try:
                schema.extend(list(self.c.getdescription()))
            except StopIteration:
                try:
                    raise
                finally:
                    try:
                        self.c.close()
                    except:
                        pass

    def close(self):
        self.c.close()
    def next(self):
        return self.iter.next()
    def __iter__(self):
        return self

class NopVT:
    def __init__(self,envdict,largs,dictargs): #DO NOT DO ANYTHING HEAVY
        self.largs=largs
        self.envdict=envdict
        self.dictargs=dictargs
        self.schema = []

        if 'query' not in dictargs:
            raise functions.OperatorError(__name__.rsplit('.')[-1],"No query argument ")
        self.query=dictargs['query']
        del dictargs['query']
    def getdescription(self):
        if self.schema==[]:
            raise functions.OperatorError(__name__.rsplit('.')[-1],"VTable getdescription called before initiliazation")
        return self.schema
    def open(self):
        return NopCursor(self.query, self.envdict['db'] , self.schema, *self.largs,**self.dictargs)
    def destroy(self):
        pass

def Source():
    return SourceVT(NopVT)

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


