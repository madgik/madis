"""
NtoN operator testvt :
sample test operator returns standar table and not matter the arguments


    >>> sql("testvt 'lo'")
    grade | name
    ---------------
    4     | Mitsos
    86    | Euterpi
    810   | Viki
    >>> sql("select * from (testvt) as a,testvt() as b")
    grade | name    | grade | name
    ---------------------------------
    4     | Mitsos  | 4     | Mitsos
    4     | Mitsos  | 86    | Euterpi
    4     | Mitsos  | 810   | Viki
    86    | Euterpi | 4     | Mitsos
    86    | Euterpi | 86    | Euterpi
    86    | Euterpi | 810   | Viki
    810   | Viki    | 4     | Mitsos
    810   | Viki    | 86    | Euterpi
    810   | Viki    | 810   | Viki

"""


from vtiterable import SourceVT
registered=False

class TestCursor:
    def __init__(self,list):
        self.iter=iter(list)
    def next(self):
        return self.iter.next()
    def __iter__(self):
        return self
    def close(self):
        pass
class TestVT:
    def __init__(self,envdict,largs,dictargs): #DO NOT DO ANYTHING HEAVY
        self.largs=largs
        self.envdict=envdict
        self.dictargs=dictargs        
    def getdescription(self):
        return [('grade',),('name',)]
    def open(self):        #RETURN DATA ITERATOR at the begining after the first call of that getdescription must return schema
        return TestCursor([[4,'Mitsos'],[86,'Euterpi'],[810,'Viki']])
    def disconnect(self):
        pass
    def destroy(self):
        pass

def Source():
    return SourceVT(TestVT)



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