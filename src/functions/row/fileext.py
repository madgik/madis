# coding: utf-8
import os.path


def fileextension(*args):

    """
    .. function:: fileextension(text) -> text

    Returns the extension of a given text argument.

    Examples:

    >>> table1('''
    ... "http://www.di.uoa.gr/lalala.gif"
    ... ''')
    >>> sql("select fileextension(a) from table1")
    fileextension(a)
    ----------------
    .gif

    """

    try:
        ret=os.path.splitext(args[0])
    except ValueError:
        return None
    
    return ret[1]

fileextension.registered=True

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
