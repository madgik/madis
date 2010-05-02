"""
.. function:: serialout(query:None,filename)

Write *query* results serialised in *filename*.

    >>> sql("select * from (file file:testing/colpref.csv dialect:csv header:t) limit 3")
    userid | colid | preference | usertype
    --------------------------------------
    agr    |       | 6617580.0  | agr
    agr    | a0037 | 2659050.0  | agr
    agr    | a0086 | 634130.0   | agr
    >>> sql("coltypes select * from (file file:testing/colpref.csv dialect:csv header:t) limit 3")
    column     | type
    -----------------
    userid     | text
    colid      | text
    preference | text
    usertype   | text
    >>> sql("serialout '../../tests/colspref.bin' typing 'preference:real' select * from (file file:testing/colpref.csv dialect:csv header:t) limit 3")
    return_value
    ------------
    1
    >>> sql("select * from serialin('../../tests/colspref.bin')")
    userid | colid | preference | usertype
    --------------------------------------
    agr    |       | 6617580.0  | agr
    agr    | a0037 | 2659050.0  | agr
    agr    | a0086 | 634130.0   | agr
    >>> sql("coltypes select * from serialin('../../tests/colspref.bin')")
    column     | type
    -----------------
    userid     | text
    colid      | text
    preference | real
    usertype   | text
"""

import setpath
from vtout import SourceNtoOne
import functions
from lib.iterutils import peekable

import struct
import cPickle

registered=True



def binData(diter,*args,**formatAgrs):
    chunksize=1000000
    maxchunksize=100000000

    addnums=False
    linechunks=False
    if ('chunksize' in formatAgrs and formatAgrs['chunksize']):
        try:
            chunksize=int(formatAgrs['chunksize'])
            if chunksize>maxchunksize:
                chunksize=maxchunksize
        except Exception:
            raise functions.OperatorError(__name__.rsplit('.')[-1],"Bad chunk size")

    if ('chunknums' in formatAgrs and formatAgrs['chunknums']):
         addnums=True
    if ('linechunks' in formatAgrs and formatAgrs['linechunks']):
        addnums=True
        linechunks=True
    if len(args)>0:
        filename=args[0]
    else:
        raise functions.OperatorError(__name__.rsplit('.')[-1],"No destination provided")
    if 'append' in formatAgrs and formatAgrs['append']:
        f=open(filename,'ab')
    else:
        f=open(filename,'wb')
    iter=peekable(diter)
    try:
        r,schema=iter.peek()
        if addnums:
            data=cPickle.dumps(schema)
            lsize=struct.pack('!i',len(data))
            f.write(lsize+data)
        else:
            cPickle.dump(schema,f)
    except StopIteration:
        f.close()
        return
    if addnums:
        if linechunks:
            for row,h in iter:
                data=cPickle.dumps(row)
                lsize=struct.pack('!i',len(data))
                f.write(lsize+data)
        else:
            data=''
            for row,h in iter:
                line=cPickle.dumps(row)
                if (len(data)+len(line))>=chunksize:
                    lsize=struct.pack('!i',len(data))
                    f.write(lsize+data)
                    data=line
            if data!='':
                lsize=struct.pack('!i',len(data))
                f.write(lsize+data)
                data=''
    else:
        for row,h in iter:
            cPickle.dump(row,f)
    f.close()

boolargs=['append','chunknums','linechunks']

def Source():
    global boolargs
    return SourceNtoOne(binData,boolargs)


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