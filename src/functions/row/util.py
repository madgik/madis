# coding: utf-8
from gzip import zlib

def gz(*args):

    """
    .. function:: gz(text) -> gzip compressed blob

    Function *gz* compresses its input with gzip's maximum compression level.

    Examples:

    >>> table1('''
    ... "qwerqewrqwerqwerqwerqwerqwer"
    ... "asdfasdfasdfasdfasdfasdfsadf"
    ... ''')
    >>> sql("select length(a), length(gz(a)) from table1")
    length(a) | length(gz(a))
    -------------------------
    28        | 20
    28        | 18

    """

    return buffer(zlib.compress(args[0], 9))

gz.registered=True

def ungz(*args):

    """
    .. function:: ungz(blob) -> text

    Function *ungz* decompresses gzip blobs. If the input blobs aren't gzip
    compressed, then it just returns them as they are.

    Examples:

    >>> table1('''
    ... "qwerqwerqwer"
    ... "asdfasdfasdf"
    ... ''')
    >>> sql("select ungz(gz(a)) from table1")
    ungz(gz(a))
    ------------
    qwerqwerqwer
    asdfasdfasdf

    >>> sql("select ungz('string'), ungz(123)")
    ungz('string') | ungz(123)
    --------------------------
    string         | 123

    """

    try:
        return zlib.decompress(args[0])
    except:
        return args[0]

ungz.registered=True

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
