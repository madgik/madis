import sys
from itertools import repeat, imap
import cPickle
import cStringIO
import struct
import zlib
import apsw
from array import array
import marshal



registered=True

class Decompression:
    
    def __init__ (self):
        self.self.blocknumberber = 0

    def decompressblockiter(self,inputblock):
        cols = self.decompressblock(inputblock)
        

        
    def decompressblock(self,inputblock):
        import bz2
        import msgpack
        serializer = msgpack
        self.self.blocknumberber += 1
        if self.self.blocknumberber == 1 :
            # schema block
            input = cStringIO.StringIO(inputblock)
            b = struct.unpack('!B',input.read(1))
            if not b[0]:
                self.schema = cPickle.load(input)
            else :
                raise error('Not a schema block!')
            yield self.schema
        else :
            colnum = len(self.schema)
            input = cStringIO.StringIO(inputblock)
            while True:
                try:
                    b = struct.unpack('!B', input.read(1))
                except:
                    break
                if b[0]:
                    decompression = struct.unpack('!B', input.read(1))
                    if decompression[0] :
                        decompress = zlib.decompress
                    else:
                        decompress = bz2.decompress

                    type = '!'+'i'*(colnum*2+1)
                    ind = list(struct.unpack(type, input.read(4*(colnum*2+1))))

                    cols = [None]*colnum
                    for c in xrange(colnum):
                        s = serializer.loads(decompress(input.read(ind[c*2])))
                        if (len(s)>1 and ind[c*2+1]==0 and ind[colnum*2]>1):
                            cols[c] = s
                        else:
                            if len(s)==1:
                                tmp = s[0]
                                cols[c] = repeat(tmp, ind[colnum*2])
                            elif len(s)<256:
                                cols[c] = imap(s.__getitem__, array('B', decompress(input.read(ind[c*2+1]))))
                            else:
                                cols[c] = imap(s.__getitem__, array('H', decompress(input.read(ind[c*2+1]))))

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
                elif not b[0]:
                    cPickle.load(input)



#class Compression:
#
#    def __init__ (self,schema,splitnum):
#        self.schema = schema
#        self.splitnum = splitnum
#        self.currentalgorithm = 'sdicc'
#        self.blocknumber = 0
#        self.comprblocknumber = 0
#        self.maxlevel = 18
#        self.compressiondict = {
#        0:('sdicc',zlib.compress,0),
#        1:('sdicc',zlib.compress,1),
#        2:('sdicc',zlib.compress,2),
#        3:('sdicc',zlib.compress,3),
#        4:('sdicc',zlib.compress,4),
#        5:('sdicc',zlib.compress,5),
#        6:('sdicc',zlib.compress,6),
#        7:('sdicc',zlib.compress,7),
#        8:('sdicc',zlib.compress,8),
#        9:('sdicc',zlib.compress,9),
#        10:('sdicc',bz2.compress,1),
#        11:('sdicc',bz2.compress,2),
#        12:('sdicc',bz2.compress,3),
#        13:('sdicc',bz2.compress,4),
#        14:('sdicc',bz2.compress,5),
#        15:('sdicc',bz2.compress,6),
#        16:('sdicc',bz2.compress,7),
#        17:('sdicc',bz2.compress,8),
#        18:('sdicc',bz2.compress,9)
#        }
#
#    def getmaxlevel(self):
#        return self.maxlevel
#
#
#
#    def compress(self):
#        returned = StringIO.StringIO()
#        returned.write(struct.pack('!B', 0))
#        cPickle.dump(schema,returned,1)
#        yield returned
#        formatArgs = (yield)
#        if 'level' in formatArgs:
#            self.compress = self.compressiondict[level][1]
#            self.level = self.compressiondict[level][2]
#            if self.compressiondict[level][0] != self.currentalgorithm:
#                self.comprblocknumber = 0
#                self.currentalgorithm = self.compressiondict[level][0]
#            if self.compressiondict[level][0] == 'sdicc':
#                sdicc(diter,schema)
#            elif self.compressiondict[level][0] == 'spac':
#                raise error('Spac not implemented yet!')
#            elif self.compressiondict[level][0] == 'cspac':
#                raise error('cSpac not implemented yet!')
#        else :
#            self.compress = zlib.compress
#            self.level = 3
#            if self.currentalgorithm != 'sdicc':
#                self.currentalgorithm = 'sdicc'
#                self.currentalgorithm = 0
#            sdicc(diter,schema)
#
#
#
#    def compress(self,diter,schema,*args,**formatArgs):
#        if 'level' in formatArgs:
#            self.compress = self.compressiondict[level][1]
#            self.level = self.compressiondict[level][2]
#            if self.compressiondict[level][0] != self.currentalgorithm:
#                self.blocknumber = 0
#                self.currentalgorithm = self.compressiondict[level][0]
#            if self.compressiondict[level][0] == 'sdicc':
#                sdicc(diter,schema)
#            elif self.compressiondict[level][0] == 'spac':
#                raise error('Spac not implemented yet!')
#            elif self.compressiondict[level][0] == 'cspac':
#                raise error('cSpac not implemented yet!')
#
#        else:
#            self.compress = zlib.compress
#            self.level = 3
#            if self.currentalgorithm != 'sdicc':
#                self.currentalgorithm = 'sdicc'
#                self.blocknumber = 0
#            sdicc(diter,schema)
#
#        self.blocknumber += 1
#
#
#
#    def sdicc(self, diter, schema):
#        returned = StringIO.StringIO()
#        output = StringIO.StringIO()
#        colnum = len(schema)
#        returned.write(struct.pack('!B', 0))
#        cPickle.dump(schema,returned,1)
#        if hasattr(sys, 'pypy_version_info'):
#            from __pypy__ import newlist_hint
#        else:
#            newlist_hint = lambda size: []
#        paxcols = []
#
#        exitGen=False
#
#        if lencols == 0:
#            (yield)
#
#
#        while not exitGen:
#            output.truncate(0)
#            mrows = newlist_hint(lencols)
#            try:
#                for i in xrange(lencols):
#                    mrows.append((yield))
#            except GeneratorExit:
#                exitGen = True
#
#            count = len(mrows)
#            output.write(struct.pack('!B', 1))
#            if compression == BZ2:
#                output.write(struct.pack('!B', 0))
#            else:
#                output.write(struct.pack('!B', 1))
#
#            headindex = [0 for _ in xrange((colnum*2)+1)]
#            type = '!'+'i'*len(headindex)
#            output.write(struct.pack(type, *headindex))
#
#            if mrows != []:
#
#                for i, col in enumerate(([x[c] for x in mrows] for c in xrange(colnum))):
#
#                    if self.blocknumber==0:
#                        s = sorted(set(col))
#                        lens = len(s)
#                        if lens>50*1.0*count/100:
#                            paxcols.append(i)
#                            l = output.tell()
#    #                            tempio.truncate(0)
#    #                            fastPickler.dump(col)
#                            output.write(compress(serializer.dumps(col),level))
#                            headindex[i*2] = output.tell() - l
#                        else:
#                            coldict = dict(((x,y) for y,x in enumerate(s)))
#                            l = output.tell()
#    #                            tempio.truncate(0)
#    #                            fastPickler.dump(s)
#                            output.write(compress(serializer.dumps(s),level))
#                            headindex[i*2] = output.tell()-l
#                            if lens>1:
#                                if lens<256:
#                                    output.write(compress(array('B',[coldict[y] for y in col]).tostring(),level))
#                                else:
#                                    output.write(compress(array('H',[coldict[y] for y in col]).tostring(),level))
#                            headindex[i*2+1] = output.tell()-l-headindex[i*2]
#                    else:
#                        if i in paxcols:
#                            l = output.tell()
#    #                            tempio.truncate(0)
#    #                            fastPickler.dump(col)
#                            output.write(compress(serializer.dumps(col),level))
#                            headindex[i*2] = output.tell() - l
#                        else:
#                            s = sorted(set(col))
#                            lens = len(s)
#                            coldict = dict(((x,y) for y,x in enumerate(s)))
#                            l = output.tell()
#    #                            tempio.truncate(0)
#    #                            fastPickler.dump(s)
#                            output.write(compress(serializer.dumps(s),level))
#                            headindex[i*2] = output.tell()-l
#                            if lens>1:
#                                if lens<256:
#                                    output.write(compress(array('B',[coldict[y] for y in col]).tostring(),level))
#                                else:
#                                    output.write(compress(array('H',[coldict[y] for y in col]).tostring(),level))
#                            headindex[i*2+1] = output.tell()-l-headindex[i*2]
#
#                self.blocknumber=1
#                headindex[colnum*2] = count
#                output.seek(0)
#                type = '!'+'i'*len(headindex)
#                output.write(struct.pack('!B', 1))
#                if compression == BZ2:
#                    output.write(struct.pack('!B', 0))
#                else:
#                    output.write(struct.pack('!B', 1))
#                output.write(struct.pack(type, *headindex))
#                cz = output.getvalue()
#                fileIter.write(struct.pack('!i',len(cz)))
#                fileIter.write(cz)
#        fileIter.close()
#
#
#
