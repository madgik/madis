__docformat__ = 'reStructuredText en'

import lib.jopts as jopts
import collections
import json

class jgroup:
    """
    .. function:: jgroup(columns)

    Groups columns of a group into a jpack.

    Example:

    >>> table1('''
    ... word1   1
    ... word2   1
    ... word3   2
    ... word4   2
    ... ''')
    >>> sql("select jgroup(a) from table1 group by b")
    jgroup(a)
    -----------------
    ["word1","word2"]
    ["word3","word4"]
    >>> sql("select jgroup(a,b) from table1")
    jgroup(a,b)
    -------------------------------------------------
    [["word1",1],["word2",1],["word3",2],["word4",2]]

    >>> table2('''
    ... [1,2]   1
    ... [3,4]   1
    ... [5,6]   2
    ... [7,8]   2
    ... ''')

    >>> sql("select jgroup(a) from table2")
    jgroup(a)
    -------------------------
    [[1,2],[3,4],[5,6],[7,8]]

    >>> sql("select jgroup(a,b) from table2")
    jgroup(a,b)
    -----------------------------------------
    [[[1,2],1],[[3,4],1],[[5,6],2],[[7,8],2]]
    """

    registered=True #Value to define db operator

    def __init__(self):
        self.outgroup=[]

    def step(self, *args):
        if len(args)==1:
            self.outgroup+=( jopts.elemfromj(args[0]) )
        else:
            self.outgroup.append( jopts.elemfromj(*args) )

    def final(self):
        return jopts.toj(self.outgroup)
    
class jgroupunion:
    """
    .. function:: jgroupunion(columns) -> jpack

    Calculates the union of the jpacks (by treating them as sets) inside a group.

    Example:

    >>> table1('''
    ... '[1,2]' 6
    ... '[2,3]' 7
    ... '[2,4]' '[8,11]'
    ... 5 9
    ... ''')
    >>> sql("select jgroupunion(a,b) from table1")
    jgroupunion(a,b)
    ----------------------
    [1,2,3,4,5,6,7,8,9,11]

    >>> sql("select jgroupunion(1)")
    jgroupunion(1)
    --------------
    1

    >>> table1('''
    ... '{"b":1, "a":1}' 6
    ... '{"c":1}' 7
    ... ''')
    >>> sql("select jgroupunion(a,b) from table1")
    jgroupunion(a,b)
    ----------------------
    [1,2,3,4,5,6,7,8,9,11]

    """

    registered=True #Value to define db operator

    def __init__(self):
        self.outgroup=collections.OrderedDict()

    def step(self, *args):
        self.outgroup.update( [(x,None) for x in jopts.fromj(*args)] )

    def final(self):
        return jopts.toj(list(self.outgroup))

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
