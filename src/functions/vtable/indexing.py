"""
N to N operator coltypes
Operator indexing

"""


import setpath
from vtiterable import SourceVT
import functions

#external_stream=True
registered=False

class ListCursor:
    def __init__(self,results):
        self.iter=iter(results)
    def __iter__(self):
        return self
    def next(self):
        return self.iter.next()
    def close(self):
        pass

class IndexingVT:
    def __init__(self,envdict,largs,dictargs): #DO NOT DO ANYTHING HEAVY
        self.largs=largs
        self.envdict=envdict
        self.dictargs=dictargs
        self.names=['recoverq']
        self.result=[]

    def getdescription(self):
        if not self.names:
            raise functions.OperatorError(__name__.rsplit('.')[-1],"VTable getdescription called before initiliazation")
        self.nonames=False
        return [(i,) for i in self.names]
    def open(self):
        #do indexing options
        return ListCursor(self.result)
    def destroy(self):
        pass


def Source():
    return SourceVT(IndexingVT)

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