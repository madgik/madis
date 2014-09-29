import sys
from itertools import repeat, imap
import cPickle
import cStringIO
import struct
import zlib
import apsw
from array import array
import marshal
import msgpack
import bz2
serializer = msgpack

registered=True

class Decompression:
    
    def __init__ (self,dbname = None):
        self.dbname = dbname
        self.blocknumber = 0
        
    def decompressblock(self,inputblock):
        self.blocknumber += 1
        if self.blocknumber == 1 :
            # schema block
            input = cStringIO.StringIO(inputblock)
            b = struct.unpack('!B',input.read(1))
            if not b[0]:
                self.schema = cPickle.load(input)
            else :
                raise error('Not a schema block!')
            
            if self.dbname is not None :

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

                self.cur, self.cursor, self.insertquery=createdb(self.dbname+".db", self.dbname, self.schema)
            return self.schema
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

                    if self.dbname is not None:
                        if hasattr(sys, 'pypy_version_info'):
                            from __pypy__ import newlist_hint

                            def izip(*iterables):
                                iterators = map(iter, iterables)
                                ilen = len(iterables)
                                res = [None] * len(iterables)
                                while True:
                                    ci = 0
                                    while ci < ilen:
                                        res[ci] = iterators[ci].next()
                                        ci += 1
                                    yield tuple(res)
                        else:
                            from itertools import izip
                            newlist_hint = lambda size: []
                        self.cursor.executemany(self.insertquery, izip(*cols))
                    else :
                        return cols

                elif not b[0]:
                    cPickle.load(fileIter)

    def finalize(self):
        list(self.cursor.execute('commit'))
        self.cur.close()



#class Decompress :
#
#    def __init__(self, dbname):
#        self.dbname = dbname
#
#    def setschema(self,inputblock):
#        input = cStringIO.StringIO(inputblock)
#        b = struct.unpack('!B',input.read(1))
#        if not b[0]:
#            self.schema = cPickle.load(input)
#        else :
#            raise error('Not a schema block!')
#
#
#        def createdb(where, tname, schema, page_size=16384):
#            c=apsw.Connection(where)
#            cursor=c.cursor()
#            list(cursor.execute('pragma page_size='+str(page_size)+';pragma cache_size=-1000;pragma legacy_file_format=false;pragma synchronous=0;pragma journal_mode=OFF;PRAGMA locking_mode = EXCLUSIVE'))
#            create_schema='create table '+tname+' ('
#            create_schema+='`'+unicode(schema[0][0])+'`'+ (' '+unicode(schema[0][1]) if schema[0][1]!=None else '')
#            for colname, coltype in schema[1:]:
#                create_schema+=',`'+unicode(colname)+'`'+ (' '+unicode(coltype) if coltype!=None else '')
#            create_schema+='); begin exclusive;'
#            list(cursor.execute(create_schema))
#            insertquery="insert into "+tname+' values('+','.join(['?']*len(schema))+')'
#            return c, cursor, insertquery
#
#        self.cur, self.cursor, self.insertquery=createdb(self.dbname+".db", self.dbname, self.schema)
#        return self.schema
#
#    def decompression(self,inputblock):
#
#        colnum = len(self.schema)
#        input = cStringIO.StringIO(inputblock)
#        while True:
#                try:
#                    b = struct.unpack('!B', input.read(1))
#                except:
#                    break
#                if b[0]:
#                    decompression = struct.unpack('!B', input.read(1))
#                    if decompression[0] :
#                        decompress = zlib.decompress
#                    else:
#                        decompress = bz2.decompress
#
#                    type = '!'+'i'*(colnum*2+1)
#                    ind = list(struct.unpack(type, input.read(4*(colnum*2+1))))
#
#                    cols = [None]*colnum
#                    for c in xrange(colnum):
#                        s = serializer.loads(decompress(input.read(ind[c*2])))
#                        if (len(s)>1 and ind[c*2+1]==0 and ind[colnum*2]>1):
#                            cols[c] = s
#                        else:
#                            if len(s)==1:
#                                tmp = s[0]
#                                cols[c] = repeat(tmp, ind[colnum*2])
#                            elif len(s)<256:
#                                cols[c] = imap(s.__getitem__, array('B', decompress(input.read(ind[c*2+1]))))
#                            else:
#                                cols[c] = imap(s.__getitem__, array('H', decompress(input.read(ind[c*2+1]))))
#
#                    self.cursor.executemany(self.insertquery, izip(*cols))
#
#                elif not b[0]:
#                    cPickle.load(fileIter)
#
#    def finalize(self):
#        list(self.cursor.execute('commit'))
#        self.cur.close()
#




