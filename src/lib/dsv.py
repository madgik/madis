import csv
import codecs
import cStringIO

"""
Differences from csv.reader module
Default dialect: SQLITE TABS DUMP
encoding parameter (default utf-8)
delimiter can be a multicaharacter string - given as extra parameter , not in dialect
......BUT IF YOUR FILE HAS THE chr(30) character(apart the delimiter) it will be disaster (or if encoding is multibyte )!!!!!!!!
"""

#many string delimiter!!!

class sqlitedmp(csv.Dialect):
    def __init__(self):
        self.delimiter="\t"
        #self.doublequote=True
        self.quotechar=None
        self.quoting=csv.QUOTE_NONE
        #self.quotechar='"'
        #self.quoting=csv.QUOTE_MINIMAL
        self.lineterminator='\n'

SQLITE_DIALECT=sqlitedmp()

class Onedel:
    def __init__(self,reader,big,one):
        self.reader=reader
        self.big=big
        self.one=one
    def next(self):
        return self.reader.next().replace(self.big,self.one)
    def __iter__(self):
        return self

#delimiter seperated values


class writer:
    """
    A CSV writer with default dialect sqlite dump files and utf8 encoding, NO multicharacter delimiter
    """
    def __init__(self,tsvfile,dialect=SQLITE_DIALECT,encoding="utf-8",**kwds):
        self.writer=UnicodeWriter(tsvfile,dialect,encoding,**kwds)
    def writerow(self,row):
        unirow=[]
        self.writer.writerow(row)
    def writerows(self,rows):
        self.writer.writerows(rows)

class reader:
    """
    A CSV reader which will iterate over lines in the CSV file "tsvfile",
    which is encoded in the given encoding.
    (with default dialect sqlite dump files and utf8 encoding, multicharacter delimiter YES)
    """
    def __init__(self,tsvfile,hasheader=False,dialect=SQLITE_DIALECT,encoding="utf-8",**kwds):
        self.hasheader=hasheader
        if not hasheader:
            self.reader=UnicodeReader(tsvfile,dialect,encoding,**kwds)
        else:
            self.reader=UnicodeDictReader(tsvfile,dialect,encoding,**kwds)
    def next(self):
        return self.reader.next()
    def __iter__(self):
        return self
    def fieldnames(self):
        if self.hasheader:
            return self.reader.fieldnames()
        return None

class UTF8Recoder:
    """
    Iterator that reads an encoded stream and reencodes the input to UTF-8
    """
    def __init__(self, f, encoding):
        self.reader = codecs.getreader(encoding)(f)

    def __iter__(self):
        return self

    def next(self):
        return self.reader.next().encode("utf-8")

class UnicodeReader:
    """
    A CSV reader which will iterate over lines in the CSV file "f",
    which is encoded in the given encoding.
    To accept multicharacter delimiters a temporal replacement with ~ character happens
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        f = UTF8Recoder(f, encoding)
        self.replace=False
        if 'delimiter' in kwds and len(kwds['delimiter'])>1:
            self.replace=True
            self.mdel=chr(30)
            self.big=kwds['delimiter']
            kwds['delimiter']=self.mdel
            self.reader = csv.reader(Onedel(f,self.big,self.mdel), dialect=dialect, **kwds)
        else:
            self.reader = csv.reader(f, dialect=dialect, **kwds)

    def next(self):
        row = self.reader.next()
        if self.replace: ##delimiter was more than one character (temporal replacements must be reversed)
            return [unicode(s.replace(self.mdel,self.big), "utf-8") for s in row]
        else:
            return [unicode(s, "utf-8") for s in row]

    def __iter__(self):
        return self

class UnicodeDictReader:
    """
    A CSV reader which will iterate over lines in the CSV file "f",
    which is encoded in the given encoding.
    To accept multicharacter delimiters a temporal replacement with ~ character happens
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        f = UTF8Recoder(f, encoding)
        self.replace=False
        if 'delimiter' in kwds and len(kwds['delimiter'])>1:
            self.replace=True
            self.mdel=chr(30)
            self.big=kwds['delimiter']
            kwds['delimiter']=self.mdel
            self.reader = csv.reader(Onedel(f,self.big,self.mdel), dialect=dialect, **kwds)
        else:
            self.reader = csv.reader(f, dialect=dialect, **kwds)
        self.fields=None

    def __readheader(self):
        if not self.fields:
            row = self.reader.next()
            self.fields=[unicode(s, "utf-8") for s in row]
    def next(self):
        if not self.fields:
            self.__readheader()
        row = self.reader.next()
        rowdict=dict()
        if self.replace:
            for field,cell in zip(self.fields,row):
                rowdict[field]=unicode(cell.replace(self.mdel,self.big), "utf-8")
        else:
            for field,cell in zip(self.fields,row):
                rowdict[field]=unicode(cell, "utf-8")
        
        return rowdict
    def fieldnames(self):
        if not self.fields:
            self.__readheader()
        return self.fields

    def __iter__(self):
        return self

def anytouni(i):

    if isinstance(i,str):
        return unicode(i)
    elif not isinstance(i,basestring):
        return unicode(repr(i))
    else:
        return i
    return unirow




##one delimiter only
class UnicodeWriter:
    """
    A CSV writer which will write rows to CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        # Redirect output to a queue
        self.queue = cStringIO.StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()

    def writerow(self, row):
        self.writer.writerow([anytouni(s).encode("utf-8") for s in row])
        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        # ... and reencode it into the target encoding
        data = self.encoder.encode(data)
        # write to the target stream
        self.stream.write(data)
        # empty queue
        self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)




def main():
    import sys
    import time    
    fname='partheaders.tsv'
    print "Test file %s" %(fname)
    print >> sys.stderr , time.strftime("%Y-%m-%d %H:%M:%S"),"\tBEGIN"

    with open('partheaders.tsv') as f:
        p=reader(f,hasheader=True)
        for line in p:
            print line
    print >> sys.stderr , time.strftime("%Y-%m-%d %H:%M:%S"),"\tEND"



if __name__ == "__main__":    
    main()
    