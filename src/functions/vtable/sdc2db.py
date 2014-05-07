import os.path
import sys
import functions
import os
from itertools import izip
import cPickle
import cStringIO
import vtbase
import functions
import struct
import vtbase
import functions
import os
import gc
import re
import zlib
### Classic stream iterator
registered=True
BLOCK_SIZE = 200000000
import apsw
from array import array

class SDC2DB(vtbase.VT):


    def VTiter(self, *args,**formatArgs):
        largs, dictargs = self.full_parse(args)
        where = None
        mode = 'row'
        input = cStringIO.StringIO()

        if 'file' in dictargs:
            where=dictargs['file']
        else:
            raise functions.OperatorError(__name__.rsplit('.')[-1],"No destination provided")
        col = 0

        filename, ext=os.path.splitext(os.path.basename(where))
        if 'cols' in dictargs:
            a = re.split(' |,| , |, | ,' , dictargs['cols'])
            column = [x for x in a if x != '']
        else:
            col = 1
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
        cursor = []
        for filenum,fileIter in enumerate(fileIterlist):
            b = struct.unpack('!B',fileIter.read(1))
            schema = cPickle.load(fileIter)
            colnum = len(schema)
            if filenum == 0:
                yield schema
                def createdb(where, tname, schema, page_size=16384):
                        c=apsw.Connection(where)
                        cursor=c.cursor()
                        list(cursor.execute('pragma page_size='+str(page_size)+';pragma cache_size=-1000;pragma legacy_file_format=false;pragma synchronous=0;pragma journal_mode=OFF;PRAGMA locking_mode = EXCLUSIVE'))
                        create_schema='create table '+tname+' ('
                        create_schema+='`'+unicode(schema[0][0])+'`'+ (' '+unicode(schema[0][1]) if schema[0][1]!=None else '')
                        for colname, coltype in schema[1:]:
                            create_schema+=',`'+unicode(colname)+'`'+ (' '+unicode(coltype) if coltype!=None else '')
                        create_schema+='); begin exclusive;'
                        list(cursor.execute(create_schema))
                        insertquery="insert into "+tname+' values('+','.join(['?']*len(schema))+')'
                        return c, cursor, insertquery
                cur, cursor, insertquery=createdb(where+".db", filename, schema)
            output = cStringIO.StringIO()
            blocknum = 0
            paxcols = {}

           

            while True:
                    output.truncate(0)
                    try:
                        b = struct.unpack('!B', fileIter.read(1))
                    except:
                        break
                    if b[0]:
                        blocksize = struct.unpack('!i', fileIter.read(4))
    #                        output.write(fileIter.read(blocksize[0]))
    #                        output.seek(0)
                        type = '!'+'i'*(colnum*2+1)
                        ind = list(struct.unpack(type, fileIter.read(4*(colnum*2+1))))
                        cols = [[] for _ in xrange(colnum)]
                        for c in xrange(colnum):
                            s = cPickle.loads(zlib.decompress(fileIter.read(ind[c*2])))
                            if (blocknum == 1 and c in paxcols) or (blocknum == 0 and len(s)>50*1.0*ind[colnum*2]/100):
                                cols[c] = s
                                if blocknum == 0:
                                    paxcols[c]=1
                            else:
                                if len(s)==1:
                                    cols[c] = [s[0] for _ in xrange(ind[colnum*2])]
                                elif len(s)<256:
                                    listptr = array('B')
                                    listptr.fromstring(zlib.decompress(fileIter.read(ind[c*2+1])))
                                    for lala in listptr:
                                        cols[c].append(s[lala])
                                else:
                                    listptr = array('H')
                                    listptr.fromstring(zlib.decompress(fileIter.read(ind[c*2+1])))
                                    for lala in listptr:
                                        cols[c].append(s[lala])
                        gc.disable()
                        cursor.executemany(insertquery, izip(*cols))
                        gc.enable()
                        blocknum = 1
                    elif not b[0]:
                        schema = cPickle.load(fileIter)
        list(cursor.execute('commit'))
        cur.close()

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



