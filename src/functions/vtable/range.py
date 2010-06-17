"""
.. function:: range([from:0,[to:10,[step:1]]])

Returns a range of integer numbers.

:Returned table schema:
    - *value* int
        Number in range.

.. note::

    The parameters can be given both named or unnamed. In unnamed mode parameter order is from,to,step.


Named parameters:

:from:
    Number to begin from. Default is 0
:to:
    Number to reach. Default is 10. The *to* number is not returned
:step:
    Step to augment the returned numbers. Default is 1

Examples::

    >>> sql("select * from range()")
    value
    -----
    0
    1
    2
    3
    4
    5
    6
    7
    8
    9
    >>> sql("select * from range('from:1','to:11')")
    value
    -----
    1
    2
    3
    4
    5
    6
    7
    8
    9
    10
    >>> sql("select * from range('from:2','to:15','step:3')")
    value
    -----
    2
    5
    8
    11
    14
    >>> sql("select * from range(1,10,2)")
    value
    -----
    1
    3
    5
    7
    9
    >>> sql("select * from range(5)")
    value
    -----
    1
    2
    3
    4
    5

"""


from vtiterable import SourceVT
registered=True

def linerange(fromv,tov,stepv):
    for i in xrange(fromv,tov,stepv):
        yield [i]

class RangeCursor:
    def __init__(self,fromv,tov,stepv):
        self.iter=linerange(fromv,tov,stepv)
    def next(self):
        return self.iter.next()
    def __iter__(self):
        return self
    def close(self):
        pass
class RangeVT:
    def __init__(self,envdict,largs,dictargs):
        self.largs=largs
        self.envdict=envdict
        self.dictargs=dictargs
        self.fromv=0
        self.tov=10
        self.stepv=1
        if 'from' in dictargs:
            self.fromv=int(dictargs['from'])
        if 'to' in dictargs:
            self.tov=int(dictargs['to'])
        if 'step' in dictargs:
            self.stepv=int(dictargs['step'])
        if len(largs)>=1:
            self.fromv=int(largs[0])
        if len(largs)>=2:
            self.tov=int(largs[1])
        if len(largs)>=3:
            self.stepv=int(largs[2])
        if len(largs)==1:
            self.fromv=1
            self.tov=int(largs[0])+1
    def getdescription(self):
        return [('value',)]
    def open(self):
        return RangeCursor(self.fromv,self.tov,self.stepv)
    def disconnect(self):
        pass
    def destroy(self):
        pass

def Source():
    return SourceVT(RangeVT,staticschema=True)



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