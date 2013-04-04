"""
.. function:: expand(query:None)

Executes the input query and returns the result expanding any multiset values returned. The returned result is produced iteratively.

:Returned table schema:
    Same as input query schema expanded with multiset functions column naming. When *as* renaming function is used at a multiset function,
    if the multiset function returns only one column it is named according to the *as* value,
    else a positive integer (1,2...n) is appended to the column name indicating column index in the multiset function result.

Examples::

    >>> table1('''
    ... James   10	2
    ... Mark    7	3
    ... Lila    74	1
    ... ''')
    >>> sql("select ontop(1,c,a,b) from table1")
    top1 | top2
    -----------
    Mark | 7
    >>> sql("select ontop(1,c,b,c) as prefs from table1")
    prefs1 | prefs2
    ---------------
    7      | 3
    >>> sql("select ontop(1,c,a) as nameontop from table1")
    nameontop
    ---------
    Mark
    
    The explicit invocation of expand function won't affect the output since it is already automatically invoked because of the multiset function ontop.
    
    >>> sql("expand expand select ontop(2,b,a) from table1")
    top1
    -----
    Lila
    James

.. doctest::
    :hide:
        
    >>> table2('''
    ... Fibi    40
    ... Monika  5
    ... Soula   17
    ... ''')
    >>> sql("select * from (select ontop(1,c,a,b) from table1) as a,(select ontop(1,c,a,b) from table1) as b,(select ontop(2,b,a,b) from table2) as c where a.top2=b.top2 and a.top2<c.top2")
    top1 | top2 | top1 | top2 | top1  | top2
    ----------------------------------------
    Mark | 7    | Mark | 7    | Fibi  | 40
    Mark | 7    | Mark | 7    | Soula | 17
    
    >>> sql("select * from (select ontop(3,c,a,b) from table1) as a,(select ontop(3,c,a,b) from table1) as b,(select ontop(2,b,a,b) from table2) as c")
    top1  | top2 | top1  | top2 | top1  | top2
    ------------------------------------------
    Mark  | 7    | Mark  | 7    | Fibi  | 40
    Mark  | 7    | Mark  | 7    | Soula | 17
    Mark  | 7    | James | 10   | Fibi  | 40
    Mark  | 7    | James | 10   | Soula | 17
    Mark  | 7    | Lila  | 74   | Fibi  | 40
    Mark  | 7    | Lila  | 74   | Soula | 17
    James | 10   | Mark  | 7    | Fibi  | 40
    James | 10   | Mark  | 7    | Soula | 17
    James | 10   | James | 10   | Fibi  | 40
    James | 10   | James | 10   | Soula | 17
    James | 10   | Lila  | 74   | Fibi  | 40
    James | 10   | Lila  | 74   | Soula | 17
    Lila  | 74   | Mark  | 7    | Fibi  | 40
    Lila  | 74   | Mark  | 7    | Soula | 17
    Lila  | 74   | James | 10   | Fibi  | 40
    Lila  | 74   | James | 10   | Soula | 17
    Lila  | 74   | Lila  | 74   | Fibi  | 40
    Lila  | 74   | Lila  | 74   | Soula | 17
"""

import setpath
import vtbase
import functions
import re
from lib.sqlitetypes import getElementSqliteType

### Classic stream iterator
registered=True

noas=re.compile('.*\(.*\).*')

class Expand(vtbase.VT):
    def VTiter(self, *parsedArgs,**envars):
        largs, dictargs = self.full_parse(parsedArgs)

        if 'query' not in dictargs:
            raise functions.OperatorError(__name__.rsplit('.')[-1],"No query argument ")
        query=dictargs['query']

        self.connection = envars['db']

        c=self.connection.cursor().execute(query, parse = False)

        schema = c.getdescription()
        self.nonames = True
        names = []
        types = []
        orignames = [x[0] for x in schema]
        origtypes = [x[1] if len(x)>1 else 'None' for x in schema]

        for row in c:
            nrow = []
            nnames = []
            ttypes=[]

            for i in xrange(len(row)):
                obj=row[i]
                if type(obj)==buffer and obj[:len(functions.iterheader)]==functions.iterheader:
                    oiter=self.connection.openiters[str(obj)]
                    try:
                        first = oiter.next()
                    except StopIteration:
                        first = [None]
                    if self.nonames:
                        ttypes+=['GUESS']*len(first)
                        if noas.match(orignames[i]):
                            if type(first)!=tuple:
                                nnames += ['C'+str(j) for j in xrange(1,len(first)+1)]
                                oiter=itertools.chain([first], oiter)
                            else:
                                nnames += list(first)
                        else:
                            if len(first)==1:
                                nnames +=[orignames[i]]
                            else:
                                nnames +=[orignames[i]+str(j) for j in xrange(1,len(first)+1)]
                    nrow += [(obj, oiter)]
                else:
                    if self.nonames:
                        ttypes += [origtypes[i]]
                        nnames += [orignames[i]]
                    nrow += [obj]

            if self.nonames:
                firstbatch = self.exprown(nrow)
                try:
                    firstrow = firstbatch.next()
                except Exception, e:
                    firstrow = []
  
                for i in ttypes:
                    if i == 'GUESS':
                        try:
                            i = getElementSqliteType(firstrow[i])
                        except Exception, e:
                            i = 'text'
                        if i == None:
                            i = 'text'
                    types.append(i)
                for i in nnames:
                    names.append(i)
                yield [(names[i], types[i]) for i in xrange(len(types))]
                self.nonames=False

                for exp in firstbatch:
                    yield exp
            else:
                for exp in self.exprown(nrow):
                    yield exp

    def exprown(self, row):
        for i in xrange(len(row)):
            iobj=row[i]
            if type(iobj)==tuple:
                for el in iobj[1]:
                    for l in self.exprown(row[(i+1):]):
                        yield list(row[:i])+list(el)+list(l)
                try:
                    del(self.connection.openiters[iobj[0]])
                except KeyboardInterrupt:
                    raise
                except:
                    pass
                return

            if hasattr(iobj,'__iter__'):
                for el in iobj:
                    for l in self.exprown(row[(i+1):]):
                        yield list(row[:i])+list(el)+list(l)
                return
        yield row

def Source():
    return vtbase.VTGenerator(Expand)

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


