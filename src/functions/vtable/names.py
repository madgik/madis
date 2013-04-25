"""
.. function:: names(query:None)

Returns column names of input query.


:Returned table schema:
    Columns are automatically named as *colname1 text, colname2 text...*


Examples::

    >>> sql("names select 5 as vt")
    colname1
    --------
    vt

    >>> sql("names select 2 as num, 7 as grade")
    colname1 | colname2
    -------------------
    num      | grade

"""


import setpath          
from vtiterable import SourceVT
import functions


registered=True

class NamesCursor:
    def __init__(self,sqlquery,connection, first , names, results):
        if first:
            connection=connection
            sqlquery=sqlquery
            c=connection.cursor()
            execit=c.execute(sqlquery)
            cols=[]
            vals=[]

            try:
                samplerow=execit.next()
            except StopIteration:
                pass

            try:
                vals=[str(v[0]) for v in c.getdescription()]
                cols=["colname"+str(i) for i in range(1,len(vals)+1)]
                results.append(vals)
                for el in cols:
                    names.append(el)
            except Exception, e:
                raise functions.OperatorError(__name__.rsplit('.')[-1],"Could not aquire schema")
            finally:
                c.close()
                
        self.iter=iter(results)

    def __iter__(self):
        return self
    def next(self):
        return self.iter.next()
    def close(self):
        pass

class NameVT:
    def __init__(self,envdict,largs,dictargs): #DO NOT DO ANYTHING HEAVY
        self.largs=largs
        self.envdict=envdict
        self.dictargs=dictargs
        self.nonames=True
        self.names=[]
        self.result=[]

        if 'query' not in dictargs:
            raise functions.OperatorError(__name__.rsplit('.')[-1]," needs query argument ")
        self.query=dictargs['query']
        del dictargs['query']
    def getdescription(self):
        if not self.names:
            raise functions.OperatorError(__name__.rsplit('.')[-1],"VTable getdescription called before initiliazation")
        self.nonames=False
        return [(i,) for i in self.names]
    def open(self):
        return NamesCursor(self.query,self.envdict['db'],self.nonames,self.names,self.result)
    def destroy(self):
        pass


def Source():
    return SourceVT(NameVT)

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