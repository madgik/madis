# To change this template, choose Tools | Templates
# and open the template in the editor.
import os.path
import setpath
import sys
import imp
from lib.dsv import writer
import gzip
from lib.ziputils import ZipIter
import functions
from lib.vtoutgtable import vtoutpugtformat
import lib.inoutparsing
import os
import apsw
from collections import defaultdict
import json
from itertools import izip
import itertools
import marshal as marshal
import cPickle
import pickle
import setpath
import vtbase
import functions
import struct
from array import array
import vtbase
import functions
import apsw
import os
import sys
import gc
#import marshal
import gc
import re
import zlib
### Classic stream iterator
registered=True
BLOCK_SIZE = 32768000


class UnionAllRC(vtbase.VT):


    def VTiter(self, *args,**formatArgs):
        largs, dictargs = self.full_parse(args)
        where = None
        mode = 'row'

        if 'file' in dictargs:
            where=dictargs['file']
        else:
            raise functions.OperatorError(__name__.rsplit('.')[-1],"No destination provided")
        col = 0

        if 'cols' in dictargs:
            a = re.split(' |,| , |, | ,' , dictargs['cols'])
            column = [x for x in a if x != '']
        else:
            col = 1


        filename, ext=os.path.splitext(os.path.basename(where))
        fullpath = str(os.path.abspath(os.path.expandvars(os.path.expanduser(os.path.normcase(where)))))
        if 'start' in dictargs and 'end' in dictargs:
            fileIterlist=[open(fullpath+"."+str(x), "rb") for x in xrange(int(dictargs['start']),int(dictargs['end'])+1)]
        else:
            fileIterlist = [open(where, "rb")]

        for filenum,fileObject in enumerate(fileIterlist):
            schema = marshal.load(fileObject)
            colnum = len(schema)
            ENDFILE = 0
            if filenum == 0:
                yield schema

            while True:
                row=0
                d = 0
                ind = [0 for _ in xrange(colnum+2)]

                if ENDFILE==1:
                    try:
                        newschema=marshal.load(fileObject)
                        ENDFILE=0
                    except EOFError:
                        break


                for i in xrange(colnum+2):
                    ind[i] = struct.unpack('L',fileObject.read(8))
                if ind[colnum+1][0] == 1:
                    ENDFILE = 1

                d2 = [[] for _ in xrange(colnum)]

                for col in xrange(colnum):
                    obj = fileObject.read(ind[col+1][0]-ind[col][0])
                    d2[col] = marshal.loads(zlib.decompress(obj))

                while True:
                    tup = []
                    for col in xrange(colnum):
                        try:
                            tup.append(d2[col][row])
                        except :
                            d = 1
                            break
                    if d == 1:
                        break
                    yield tup
                    tup = []
                    row+=1




        try:
            for fileObject in fileIterlist:
                fileObject.close()
        except NameError:
            pass


def Source():
    return vtbase.VTGenerator(UnionAllRC)

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


