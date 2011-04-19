"""
.. function:: clipout(query:None)

Writes in clipboard the output of *query*.

:Returned table schema:
    - *return_value* int
        Boolean value 1 indicating success. On failure an exception is thrown.

Examples:

    >>> sql("clipout select 5,6")
    return_value
    ------------
    1
"""

import setpath
from vtout import SourceNtoOne
import os
import functions

registered=True

def Clipout(diter):
    import lib.pyperclip as clip
    a=[]

    for row,header in diter:
        a.append(u'\t'.join([unicode(unicode(i).replace('\t','    ')).encode('utf-8', 'replace') for i in row]))

    if os.name == 'nt':
        clip.setcb(functions.mstr('\n'.join(a)))
    else:
        clip.setcb('\n'.join(a))

def Source():
    return SourceNtoOne(Clipout)

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