from datetime import datetime, timedelta
from pytz import timezone
import pytz
from dateutil import parser




def tzconverter(*args):

    """
    .. function:: tzconverter(timestamp,sourcetz, targettz,format)

    Returns timestamps converted from source timezone to target timezone. The timestamps are returned in ISO format


    Example::

    >>> table1('''
    ... "12.05.2010 00:00:00"
    ... "12.05.2010 00:01:00"
    ... "12.05.2010 00:02:00"
    ... ''')

    ... ''')
    >>> sql("select a, tzconverter(a,'Europe/Berlin','UTC')  from table1 ")
    a                   | tzconverter(a,'Europe/Berlin','UTC')
    ----------------------------------------------------------
    12.05.2010 00:00:00 | 2010-12-04T23:00:00+00:00
    12.05.2010 00:01:00 | 2010-12-04T23:01:00+00:00
    12.05.2010 00:02:00 | 2010-12-04T23:02:00+00:00


    """

    date_str = args[0]

    source_tz = timezone(args[1])
    target_tz = timezone(args[2])

    date = parser.parse(date_str, fuzzy=True)

    datetime_obj_converted = date.replace(tzinfo=source_tz)

    result = datetime_obj_converted.astimezone(target_tz).isoformat();

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
