"""
.. function:: expand(query:None)

Executes the input query and returns the result expanding any multiset values returned. The returned result is produced iteratively.

.. toadd See also PRODUCTIVITY.. LINK

.. note::

    For queries including functions declared as multiset expand function is called automatically. So there is no need to use this function explicitly in queries.

.. toadd LINK multiset LINK CompBuffer

:Returned table schema:
    Same as input query schema expanded with multiset functions column naming. When *as* renaming function is used at a multiset function, if the multiset function returns only one column it is named according to the *as* value, differently a positive integer (1,2...n) is appended to the column name indicating column index in the multiset function result.


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
    James
    Lila

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
    Mark | 7    | Mark | 7    | Soula | 17
    Mark | 7    | Mark | 7    | Fibi  | 40
    >>> sql("select * from (select ontop(3,c,a,b) from table1) as a,(select ontop(3,c,a,b) from table1) as b,(select ontop(2,b,a,b) from table2) as c")
    top1  | top2 | top1  | top2 | top1  | top2
    ------------------------------------------
    Lila  | 74   | Lila  | 74   | Soula | 17
    Lila  | 74   | Lila  | 74   | Fibi  | 40
    Lila  | 74   | James | 10   | Soula | 17
    Lila  | 74   | James | 10   | Fibi  | 40
    Lila  | 74   | Mark  | 7    | Soula | 17
    Lila  | 74   | Mark  | 7    | Fibi  | 40
    James | 10   | Lila  | 74   | Soula | 17
    James | 10   | Lila  | 74   | Fibi  | 40
    James | 10   | James | 10   | Soula | 17
    James | 10   | James | 10   | Fibi  | 40
    James | 10   | Mark  | 7    | Soula | 17
    James | 10   | Mark  | 7    | Fibi  | 40
    Mark  | 7    | Lila  | 74   | Soula | 17
    Mark  | 7    | Lila  | 74   | Fibi  | 40
    Mark  | 7    | James | 10   | Soula | 17
    Mark  | 7    | James | 10   | Fibi  | 40
    Mark  | 7    | Mark  | 7    | Soula | 17
    Mark  | 7    | Mark  | 7    | Fibi  | 40
"""



import setpath
import functions
from lib.buffer import CompBuffer

from vtiterable import SourceVT
from lib.iterutils import peekable
from lib.sqlitetypes import getElementSqliteType
import re

registered=True

noas=re.compile('.*\(.*\).*')

class ExpCursor:
    def __init__(self,connection,first,names,types,query):
        self.cursor=connection.cursor()        
        self.names=names
        self.types=types
        self.nonames=first
        self.destroylist=[]     
        self.it=peekable(self._expanditern(self.cursor.execute(query,parse=False),self.cursor.getdescription))
        if self.nonames:
            try:
                exampleline=self.it.peek()
                for i in xrange(len(self.types)):
                    if self.types[i]=="GUESS":
                        self.types[i]=getElementSqliteType(exampleline[i])
            except StopIteration: #if StopIteration but names are discovered, meaning that Compbuffers where empty return schema                
                if self.names==[]:                    
                    raise

    def __iter__(self):
        return self
    def _expanditern(self,iter, descrfun):
        names = []
        for row in iter:
            if self.nonames:
                names = [x[0] for x in descrfun()]
                types = [x[1] if len(x)>1 else 'None' for x in descrfun()]
            nrow = []
            nnames = []
            ttypes=[]
            destroylist = []
            for i in xrange(len(row)):
                compressedobj = CompBuffer.deserialize(row[i])
                if compressedobj:
                    f = compressedobj.getfile()
                    if f:
                        destroylist += [f]
                    first = compressedobj.next()
                    if self.nonames:
                        ttypes+=['GUESS']*len(first)
                        if noas.match(names[i]):
                            nnames += list(first)
                        else:
                            if len(first)==1:
                                nnames +=[names[i]]
                            else:
                                nnames +=[names[i]+str(j) for j in xrange(1,len(first)+1)]
                    nrow += [compressedobj]
                else:
                    if self.nonames:
                        ttypes += [types[i]]
                        nnames += [names[i]]
                    nrow += [row[i]]
            if self.nonames:
                for i in ttypes:
                    self.types.append(i)
                for i in nnames:
                    self.names.append(i)
                self.destroylist=destroylist
                self.nonames=False            
            for exp in exprown(nrow):
                yield exp
    def next(self):        
        return self.it.next()
    def close(self):      
        destroy(self.destroylist)
        self.cursor.close()
        


class ExpandVT:
    def __init__(self,envdict,largs,dictargs): #DO NOT DO ANYTHING HEAVY
        self.largs=largs
        self.envdict=envdict
        self.dictargs=dictargs
        self.nonames=True
        self.names=[]
        self.types=[]
        if 'query' not in dictargs:
            raise functions.OperatorError(__name__.rsplit('.')[-1],"needs query argument ")
        self.query=dictargs['query']
        del dictargs['query']     
    def getdescription(self):
        if not self.names:
            raise functions.OperatorError(__name__.rsplit('.')[-1],"VTable getdescription called before initiliazation")
        self.nonames=False
        return [(i,j) for i,j in zip(self.names,self.types)]
    def open(self):
        return ExpCursor(self.envdict['db'],self.nonames,self.names,self.types,self.query)
    def destroy(self):
        pass

def Source():
    return SourceVT(ExpandVT)

def destroy(files):
    import os
    for f in files:
        os.remove(f)

def exprown(row):
    for i in xrange(len(row)):
        compressedobj=row[i]
        if hasattr(compressedobj,'__iter__'):
            for el in compressedobj:
                for l in exprown(row[(i+1):]):
                    yield list(row[:i])+list(el)+list(l)
            return
    yield row

"""
Example
create virtual table ontopview using expand("select userid,ontop(3,preference,collid,preference) from colpreferences group by userid");
select userid, top1, top2 from (select userid,ontop(3,preference,collid,preference) from colpreferences group by userid) order by top2 ;
"""


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