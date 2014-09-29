import os.path
import sys
import functions
import os
from itertools import repeat, imap
import cPickle
import cStringIO
import vtbase
import functions
import struct
import vtbase
import os
import re
import zlib
import apsw
from array import array
import marshal
import msgpack
import bz2
from decompression import Decompression

if hasattr(sys, 'pypy_version_info'):
    from __pypy__ import newlist_hint

    def izip(*iterables):
        # izip('ABCD', 'xy') --> Ax By
        iterators = tuple(map(iter, iterables))
        ilen = len(iterables)
        res = [None] * ilen
        while True:
            ci = 0
            while ci < ilen:
                res[ci] = iterators[ci].next()
                ci += 1
            yield res
else:
    from itertools import izip
    newlist_hint = lambda size: []

serializer = msgpack

registered=True



def imapm(function, iterable):
    # imap(pow, (2,3,10), (5,2,3)) --> 32 9 1000
    it = iter(iterable)
    while True:
        yield function(it.next())

def repeatm(object, times):
    for i in xrange(times):
        yield object

class SDC2DB(vtbase.VT):

    def VTiter(self, *args,**formatArgs):
        largs, dictargs = self.full_parse(args)
        where = None

        if 'file' in dictargs:
            where=dictargs['file']
        else:
            raise functions.OperatorError(__name__.rsplit('.')[-1],"No destination provided")

        filename, ext=os.path.splitext(os.path.basename(where))
        start = 0
        end = sys.maxint-1
        if 'start' in dictargs:
            start = int(dictargs['start'])
        if 'end' in dictargs:
            end = int(dictargs['end'])

        fullpath = str(os.path.abspath(os.path.expandvars(os.path.expanduser(os.path.normcase(where)))))

        fileIterlist = []
        for x in xrange(start,end+1):
            try:
                fileIterlist.append(open(fullpath+"."+str(x), "rb"))
            except:
                break

        if fileIterlist == []:
            try:
                fileIterlist = [open(where, "rb")]
            except :
                raise  functions.OperatorError(__name__.rsplit('.')[-1],"No such file")

        decomp = Decompression()
        
        for filenum,fileIter in enumerate(fileIterlist):
            i = 0
            while True:
                i += 1
                try:
                    blocksize = struct.unpack('!i', fileIter.read(4))
                except:
                    break
                if i == 1:
                    yield decomp.decompressblock(fileIter.read(blocksize[0]))
                else :
                    cols = decomp.decompressblock(fileIter.read(blocksize[0]))
                    if hasattr(sys, 'pypy_version_info'):
                        iterators = tuple(map(iter, cols))
                        ilen = len(cols)
                        res = [None] * ilen

                        while True:
                            ci = 0
                            try:
                                while ci < ilen:
                                    res[ci] = iterators[ci].next()
                                    ci += 1
                                yield res
                            except:
                                break

                    else:
                        for row in izip(*cols):
                            yield row
        #decomp.finalize()
                    

        
        
        try:
            for fileObject in fileIterlist:
                fileObject.close()
        except NameError:
            pass

def Source():
    return vtbase.VTGenerator(SDC2DB)

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



