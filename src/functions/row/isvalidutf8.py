# coding: utf-8

import re

# Every regular expression containing \W \w \D \d \b \S \s needs to be compiled
# like below. If you want to embed the UNICODE directive inside the
# regular expression use:
# (?u) like re.sub(ur'(?u)[\W\d]', ' ', o)
query_regular_characters=re.compile(ur"""^[("„”“‘’´«»’ʹ–\w\s\[!-~\]\[\u0030-\u03d6\]]*$""", re.UNICODE)

def isvalidutf8(*args):

    """
    .. function:: isvalidutf8(text) -> 1/0
    
    Returns 1 if the input text is in valud UTF-8 format, or 0 if not.
    This function is used to find corrupted UTF-8 strings.

    Examples:

    >>> table1('''
    ... test
    ... δοκιμή!
    ... sÃ©vignÃ
    ... Ã©vezred
    ... ''')
    >>> sql("select isvalidutf8(a) from table1")
    isvalidutf8(a)
    --------------
    1
    1
    0
    0        
    """

    for i in args:
        if i==None:
            return 0
        if not query_regular_characters.match(i):
            return 0

    return 1

isvalidutf8.registered=True


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
