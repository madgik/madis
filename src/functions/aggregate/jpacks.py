__docformat__ = 'reStructuredText en'

import lib.jlist as jlist

class jgroup:
    """
    .. function:: concatgroup(X)

    Concatenates strings in a group/dataset X.

    Example:

    >>> table1('''
    ... word1   1
    ... word2   1
    ... word3   2
    ... word4   2
    ... ''')
    >>> sql("select jgroup(a) from table1 group by b")
    jgroup(a)
    ------------------
    ["word1", "word2"]
    ["word3", "word4"]
    >>> sql("select jgroup(a,b) from table1")
    jgroup(a,b)
    ------------------------------------------------------------------------
    ["[\"word1\", 1]", "[\"word2\", 1]", "[\"word3\", 2]", "[\"word4\", 2]"]
    """

    registered=True #Value to define db operator

    def __init__(self):
        self.outgroup=[]

    def step(self, *args):
        self.outgroup.append(jlist.toj(args))

    def final(self):
        return jlist.toj(self.outgroup)


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
