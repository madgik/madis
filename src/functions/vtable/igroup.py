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
import vtbase
import functions

### Classic stream iterator
registered=True
       
class IGroup(vtbase.VT):
    def BestIndex(self, constraints, orderbys):
        return (None, 0, None, True, 1000)

    def VTiter(self, *parsedArgs,**envars):
        largs, dictargs = self.full_parse(parsedArgs)

        if 'query' not in dictargs:
            raise functions.OperatorError(__name__.rsplit('.')[-1],"No query argument ")
        query=dictargs['query']

        c=envars['db'].cursor().execute(query)

        try:
            yield list(c.getdescription())
        except StopIteration:
            try:
                raise
            finally:
                try:
                    c.close()
                except:
                    pass

        for r in c:
            yield r

def Source():
    return vtbase.VTGenerator(IGroup)

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


