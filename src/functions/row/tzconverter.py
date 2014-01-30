from datetime import datetime, timedelta
from pytz import timezone
import pytz



def tzconverter(*args):

    """
    .. function:: jaccard(jpack1,jpack2)

    Return jaccard similarity value of two jpacks.

    Example:

    >>> table1('''
    ... "12/05/2010 00:00:00"
    ... "12/05/2010 00:01:00"
    ... "12/05/2010 00:02:00"
    ... ''')

    ... ''')
    >>> sql("select a, tzconverter(a,'Europe/Berlin','UTC','%d/%m/%Y %H:%M:%S')  from table1 ")
    a                   | tzconverter(a,'Europe/Berlin','UTC','%d/%m/%Y %H:%M:%S')
    ------------------------------------------------------------------------------
    12/05/2010 00:00:00 | 11/05/2010 23:00:00
    12/05/2010 00:01:00 | 11/05/2010 23:01:00
    12/05/2010 00:02:00 | 11/05/2010 23:02:00

    >>> table1('''
    ... "12.05.2010 00:00:00"
    ... "12.05.2010 00:01:00"
    ... "12.05.2010 00:02:00"
    ... ''')

    ... ''')
    >>> sql("select a, tzconverter(a,'Europe/Berlin','UTC')  from table1 ")
    a                   | tzconverter(a,'Europe/Berlin','UTC')
    ----------------------------------------------------------
    12.05.2010 00:00:00 | 11.05.2010 23:00:00
    12.05.2010 00:01:00 | 11.05.2010 23:01:00
    12.05.2010 00:02:00 | 11.05.2010 23:02:00


    """

    date_str = args[0]

    source_tz = timezone(args[1])
    target_tz = timezone(args[2])

    try:
        fmt = args[3]
    except IndexError:
        fmt = "%d.%m.%Y %H:%M:%S"

    datetime_obj = datetime.strptime(date_str, fmt)
    datetime_obj_berlin = datetime_obj.replace(tzinfo=source_tz)

    result = datetime_obj_berlin.astimezone(target_tz).strftime(fmt);

    return result

tzconverter.registered = True



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
