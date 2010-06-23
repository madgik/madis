import Queue
import setpath
import functions
from lib import iso8601

__docformat__ = 'reStructuredText en'

def timedelta2millisec(tdelta):
    return tdelta.days*24*60*60*1000+tdelta.seconds*1000+tdelta.microseconds/1000

class mindtdiff:
    """
    .. function:: mindtdiff(date)

    Returns the minimum difference *date* values of the group in milliseconds. Input dates should be in :ref:`ISO 8601 format <iso8601>`.

    Examples:

    >>> table1('''
    ... '2007-01-01 00:03:13'
    ... '2007-01-01 00:03:27'
    ... '2007-01-01 00:03:36'
    ... '2007-01-01 00:04:39'
    ... '2007-01-01 00:04:40'
    ... '2007-01-01 00:04:49'
    ... ''')
    >>> sql("select mindtdiff(a) from table1")
    mindtdiff(a)
    ------------
    1000

.. doctest::
    :hide:
    
    >>> sql("select mindtdiff(a) from (select '2005-01-01' as a) ")
    mindtdiff(a)
    ------------
    None
    >>> sql("select mindtdiff(a) from (select 5 as a where a!=5) ")
    mindtdiff(a)
    ------------
    None
    
    """
    registered=True

    def __init__(self):
        self.dates=Queue.PriorityQueue()

    def step(self, *args):
        if not args:
            raise functions.OperatorError("mindtdiff","No arguments")
        dt=iso8601.parse_date(args[0])
        self.dates.put_nowait(dt)



    def final(self):
        mindiff=None
        dtp=None
        if not self.dates:
            return
        while not self.dates.empty():
            if not mindiff:
                if not dtp:
                    dtp=self.dates.get_nowait()
                    continue
            dt=self.dates.get_nowait()
            diff=timedelta2millisec(dt-dtp)            
            if mindiff==None:
                mindiff=diff
            elif mindiff>diff:
                mindiff=diff
            dtp=dt
            import types
            
        return mindiff

class avgdtdiff:
    """
    .. function:: avgdtdiff(date)

    Returns the average difference *date* values of the group in milliseconds. Input dates should be in :ref:`ISO 8601 format <iso8601>`.

    Examples:
    
    >>> table1('''
    ... '2007-01-01 00:04:37'
    ... '2007-01-01 00:04:39'
    ... '2007-01-01 00:04:40'
    ... '2007-01-01 00:04:49'
    ... ''')
    >>> sql("select avgdtdiff(a) from table1")
    avgdtdiff(a)
    ------------
    3000.0


.. doctest::
    :hide:


    >>> sql("select avgdtdiff(a) from (select '2005-01-01' as a) ")
    avgdtdiff(a)
    ------------
    None
    >>> sql("select avgdtdiff(a) from (select 5 as a where a!=5) ")
    avgdtdiff(a)
    ------------
    None
    """
    registered=True

    def __init__(self):
        self.dates=Queue.PriorityQueue()

    def step(self, *args):
        if not args:
            raise functions.OperatorError("avgdtdiff","No arguments")
        dt=iso8601.parse_date(args[0])
        self.dates.put_nowait(dt)



    def final(self):
        avgdiff=0
        cntdiff=0
        dtp=None        
        while not self.dates.empty():
            if avgdiff==0:
                if not dtp:
                    cntdiff+=1
                    dtp=self.dates.get_nowait()
                    continue
            dt=self.dates.get_nowait()
            diff=timedelta2millisec(dt-dtp)
            cntdiff+=1
            avgdiff+=diff
            dtp=dt
        if cntdiff<2:
            return None
        return float(avgdiff)/cntdiff

        
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
        