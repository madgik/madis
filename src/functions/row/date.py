# coding: utf-8
import functions
import datetime
from lib import iso8601


def activityindex(*args):

    """
    .. function:: activityIndex(date, c1, c2) -> int

    Specialized function that classifies the provided date argument into a 6-point scale (0 to 5)

    Examples:

    >>> table1('''
    ... '2009-01-01T01:32:03Z'
    ... '2010-01-01T00:03:13Z'
    ... '2010-12-31T00:03:13Z'
    ... '2011-04-01T00:03:13Z'
    ... ''')
    >>> sql("select activityIndex(a) from table1")
    activityIndex(a)
    ----------------
    0
    1
    3
    5
    """
    now = datetime.datetime.now()
    now = iso8601.parse_date(now.strftime("%Y-%m-%d %H:%M:%S"))
    d = args[0].replace('T',' ')
    dt = iso8601.parse_date(args[0].replace('Z',''))  
    diff=now-dt

    if (diff.days)<30:
                    return 5
    elif (diff.days)<3*30:
                    return 4
    elif (diff.days)<6*30:
                    return 3
    elif (diff.days)<12*30:
                    return 2
    elif (diff.days)<24*30:
                    return 1
    elif (diff.days)>=24*30:
                    return 0
    else:
        return -1;

activityindex.registered=True

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
