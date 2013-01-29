"""

.. function:: rowidvt(query:None)

Returns the query input result adding rowid number of the result row.

:Returned table schema:
    Same as input query schema with addition of rowid column.

    - *rowid* int
        Input *query* result rowid.    

Examples::

    >>> table1('''
    ... James   10	2
    ... Mark    7	3
    ... Lila    74	1
    ... ''')
    >>> sql("rowidvt select * from table1")
    rowid | a     | b  | c
    ----------------------
    1     | James | 10 | 2
    2     | Mark  | 7  | 3
    3     | Lila  | 74 | 1
    >>> sql("rowidvt select * from table1 order by c")
    rowid | a     | b  | c
    ----------------------
    1     | Lila  | 74 | 1
    2     | James | 10 | 2
    3     | Mark  | 7  | 3

    Note the difference with rowid table column.

    >>> sql("select rowid,* from table1 order by c")
    rowid | a     | b  | c
    ----------------------
    3     | Lila  | 74 | 1
    1     | James | 10 | 2
    2     | Mark  | 7  | 3
"""
import setpath
from vtiterable import SourceVT
from lib.iterutils import peekable
import itertools
import functions

### Classic stream iterator
registered=True
       
class RowidCursor:
    def __init__(self,sqlquery,connection,first,names,types):
        self.sqlquery=sqlquery
        self.connection=connection
        self.c=self.connection.cursor()

        self.cols=names
        self.types=types
        if first:
            first = False
            ### Find names and types
            execit=peekable(self.c.execute(self.sqlquery))
            try:
                samplerow=execit.peek()
            except StopIteration:
                pass

            schema = self.c.getdescription()
            qnames=[str(v[0]) for v in schema]
            qtypes=[str(v[1]) for v in schema]
            qnames[:0]=['rowid']
            qtypes[:0]=['integer']

            ### Set names and types
            for i in qnames:
                self.cols.append(i)
            for i in qtypes:
                self.types.append(i)

            self.iter=( [x]+list(y) for x,y in itertools.izip(itertools.count(1), execit) )
        else:
            self.iter=( [x]+list(y) for x,y in itertools.izip(itertools.count(1), self.c.execute(self.sqlquery)) )

    def close(self):
        self.c.close()
    def next(self):
        return self.iter.next()
    def __iter__(self):
        return self

class RowidVT:
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
        return RowidCursor(self.query,self.envdict['db'],self.nonames,self.names,self.types,*self.largs,**self.dictargs)
    def destroy(self):
        pass



def Source():
    return SourceVT(RowidVT)



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


