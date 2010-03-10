import StringIO ,cPickle , tempfile ,gzip , os , struct
from zlib import compress, decompress
class BufferException(Exception):
    pass

def mempack(obj):
    """
    >>> a={1:'la',2:'l'}
    >>> a==memunzip(memzip(a))
    True
    >>> a=dict([(i,i) for i in xrange(2000)])
    >>> import sys
    >>> print "Compressed size / Initial size: %s%%" %(int(sys.getsizeof(memzip(a))*100/(sys.getsizeof(a)*1.0)))
    Compressed size / Initial size: 27%
    """
    return buffer(compress(cPickle.dumps(obj),9))

def memunpack(obj):
    return cPickle.loads(decompress(obj))

def emptyBuffer(header):
    a=CompBuffer()
    a.writeheader([str(header)])
    a.write([None])
    return a.serialize()

class CompBuffer:
    __header="BLOB"+chr(30)
    __fheader="FILE"+chr(30)
    __wmode=1
    __rmode=2
    __cmode=3
    def __init__(self,maxsize=30000000):
        self.strstream=StringIO.StringIO()
        self.stream=gzip.GzipFile(mode="wb",fileobj=self.strstream)
        self.maxsize=maxsize
        self.name=None
        self.mode=CompBuffer.__wmode
        self.hasheader=False
    def writeheader(self,s):
        self.hasheader=True
        self.write(s)

    def write(self,s):
        if self.mode!=self.__wmode:
            self.__modeError()
        if not self.hasheader:
            raise BufferException("Buffer has no header element")
        cPickle.dump(s,self.stream)
        if self.stream.tell()>=self.maxsize and not self.name:
            fd , fname =tempfile.mkstemp(suffix="kill.gz")
            self.name=fname
            f=os.fdopen(fd,"wb")
            self.stream.close()

            #Copy String stream to TempFile
            self.strstream.seek(0)
            inp=self.strstream.read()
            while inp:
                f.write(inp)
                inp=self.strstream.read()

            self.stream=gzip.GzipFile(mode="wb",fileobj=f)
            self.strstream.close()
            self.strstream=f

    def read(self):
        if self.mode!=self.__rmode:
            self.__modeError()
        return cPickle.load(self.stream)

    def next(self):
        try:
            return self.read()
        except EOFError:
            raise StopIteration

    def __iter__(self):
        return self

    def __modeError(self):
        if self.mode==self.__cmode:
            raise Exception("Cannot perform operation in closed stream")
        if self.mode==self.__rmode:
            raise Exception("Cannot perform operation in read only stream")
        if self.mode==self.__wmode:
            raise Exception("Cannot perform operation in write only stream")

    def serialize(self): #and close
        if self.mode!=self.__wmode:
            self.__modeError()
        v=self.__header
        self.stream.close()
        if self.name:
            v+=self.__fheader+self.name
            self.strstream.close()
        else:
            self.strstream.seek(0)
            v+=cPickle.dumps(self.strstream.read())
            self.strstream.close() #### Is it correct?
        self.mode=CompBuffer.__cmode
        return v
    def getfile(self):
        if self.mode!=self.__rmode:
            self.__modeError()
        return self.dfile

    @staticmethod
    def deserialize(obj):
        import types
        if type(obj) not in types.StringTypes or not obj.startswith(CompBuffer.__header):
            return False
        obj=str(obj)
        ptr=obj[len(CompBuffer.__header):]
        bf=CompBuffer()
        bf.dfile=None
        if ptr.startswith(CompBuffer.__fheader):
            ptr=ptr[len(CompBuffer.__fheader):]
            bf.dfile=ptr
            bf.stream=gzip.GzipFile(filename=ptr,mode="rb")
        else:
            bf.strstream=StringIO.StringIO(cPickle.loads(ptr))
            bf.strstream.seek(0)
            bf.stream=gzip.GzipFile(mode="rb",fileobj=bf.strstream)
        bf.mode=CompBuffer.__rmode
        return bf


    def close(self):
        self.stream.close()
        self.strstream.close()

#
##example USage:
#if __name__ == "__main__":
#    b=CompBuffer()
##    hugee=[1]*10000
# #   b.write(hugee)
#    b.write("lolita")
#    b.write("litsa")
#    b.write("kitsa")
##    dps=b.serialize()
#    b.read()
##    b.close()
##    b.write("Please crash")
#    dpsbad=b.serialize()
##    del b
#    bb=CompBuffer.deserialize(dps)
#    print "Output:"
#    for i in bb:
#        print i

"""
sb=StringIO.StringIO()
la=gzip.GzipFile(mode='wb',fileobj=sb)
cPickle.dump("i lola paei sxoleio",la)
cPickle.dump("o kitsos pazei",la)
#la.write("litsa")
la.close()
sb.seek(0)
#pickled=cPickle.dumps(sb.getvalue())
#la=gzip.GzipFile(mode='rb',fileobj=StringIO.StringIO(cPickle.loads(pickled)))

la=gzip.GzipFile(fileobj=StringIO.StringIO(sb.getvalue()))
#la.read()
cPickle.load(la)
cPickle.load(la)
"""


if __name__ == "__main__":
    import doctest
    doctest.testmod()