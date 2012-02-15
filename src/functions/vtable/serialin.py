"""
.. function:: serialin(location)

Read input *location* file that serialised table values, probably produced by :func:`~functions.vtable.serialout.serialout` function.

"""
#TODO Make it capable of reading multiline chunknum serialised


registered=True
external_stream=True

from vtiterable import SourceVT

import functions
import struct
import cPickle

def deserialize(fileiter,hasnums):
    if not hasnums:
        while True:
            try:
                yield cPickle.load(fileiter)
            except EOFError:
                return

    while True:
        linelens=fileiter.read(4)
        if len(linelens)==0:
            return
        if len(linelens)<4:
            raise functions.OperatorError(__name__.rsplit('.')[-1],"Bad file format")
        linelen=struct.unpack('!i', linelens)[0]
        line=fileiter.read(linelen)
        if len(line)<linelen:
            raise functions.OperatorError(__name__.rsplit('.')[-1],"Bad file format")        
        yield cPickle.loads(line)


class BininCursor:
    def __init__(self,first,names,types,*largs,**kargs):
        addnums=False
        if 'chunknums' in kargs and kargs['chunknums']:
            addnums=True
        self.cols=names
        self.types=types
        if len(largs)>0:
            filename=largs[0]
        else:
            raise functions.OperatorError(__name__.rsplit('.')[-1],"No destination provided")
        self.f=open(filename,'rb')
        self.iter=deserialize(self.f,addnums)
        if first:
            first = False
            try:
                ### Find names and types

                headers=self.iter.next()
                qnames=[str(v[0]) for v in headers]
                qtypes=[str(v[1]) for v in headers]

                ### Set names and types
                for i in qnames:
                    self.cols.append(i)
                for i in qtypes:
                    self.types.append(i)

            except StopIteration:
                try:
                    raise
                finally:
                    try:
                        self.c.close()
                    except:
                        pass
    def next(self):
        return self.iter.next()
    def __iter__(self):
        return self
    def close(self):
        self.f.close()

class BininVT:
    def __init__(self,envdict,largs,dictargs): #DO NOT DO ANYTHING HEAVY
        self.largs=largs
        self.envdict=envdict
        self.dictargs=dictargs
        self.nonames=True
        self.names=[]
        self.types=[]

    def getdescription(self):
        if not self.names:
            raise functions.OperatorError(__name__.rsplit('.')[-1],"VTable getdescription called before initiliazation")
        self.nonames=False
        return [(i,j) for i,j in zip(self.names,self.types)]
    def open(self):
        return BininCursor(self.nonames,self.names,self.types,*self.largs,**self.dictargs)
    def destroy(self):
        pass

def Source():
    return SourceVT(BininVT)


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
        