"""
.. function:: serialout(query:None,filename)

Write *query* results serialised in *filename*.

"""

import setpath
from vtout import SourceNtoOne
import functions
from lib.iterutils import peekable

import struct
import cPickle

registered=True



def binData(diter,*args,**formatAgrs):
    
    if len(args)>0:
        filename=args[0]
    else:
        raise functions.OperatorError(__name__.rsplit('.')[-1],"No destination provided")
    f=open(filename,'wb')
    iter=peekable(diter)
    try:
        r,schema=iter.peek()
        data=cPickle.dumps(schema)
        lsize=struct.pack('!i',len(data))
        f.write(lsize+data)
    except StopIteration:
        f.close()
        return

    for row,h in iter:
        data=cPickle.dumps(row)
        lsize=struct.pack('!i',len(data))
        f.write(lsize+data)
        
    f.close()


def Source():
    
    return SourceNtoOne(binData)


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