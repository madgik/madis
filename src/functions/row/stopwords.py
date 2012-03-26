# coding: utf-8

import re
import setpath
from lib import stopwordlist


def filterstopwords(*args):

    """
    .. function:: filterstopwords(str) -> str

    Returns the input text with the stopwords removed

    Examples:

    >>> table1('''
    ... 'this and wood'         'no more words'
    ... 'no more stop words'    'more free time'
    ... ''')
    >>> sql("select filterstopwords(a,b) from table1")
    filterstopwords(a,b)
    --------------------
    wood words
    stop words free time
    """

    out=[]
    for i in args:
        o=i.lower()
        o=o.strip()
        o=o.split(' ')

        for k in o:
            if len(k)>0:
                if k not in stopwordlist.stopwords:
                    out.append(k)

    return ' '.join(out)

filterstopwords.registered=True

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
