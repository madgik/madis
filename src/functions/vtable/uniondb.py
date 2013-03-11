"""
.. function:: uniondb(db_filename)

This function returns the contents of a table that has been split using OUTPUT split functionality.

Its input are DBs with names such as:

  dbname.0.db
  dbname.1.db
  ...

It is assumed that inside each of above DBs, a table named as *dbname* will exist. All of these
tables should have the same schema

"""
import vtiters
import functions
import apsw
import os

registered=True

class UnionDB(vtiters.SchemaFromArgsVT):
    def __init__(self):
        self.xcursor=None
        self.xcon=None

    def getschema(self, *parsedArgs,**envars):
        opts=self.full_parse(parsedArgs)

        self.query=None
        tablename=None

        if 'tablename' in opts[1]:
            tablename=opts[1]['tablename']

        if 'table' in opts[1]:
            tablename=opts[1]['table']

        try:
            self.query=opts[1]['query']
        except:
            pass
            
        try:
            dbname=opts[0][0]
        except:
            raise functions.OperatorError(__name__.rsplit('.')[-1],"A DB filename should be provided")

        if self.query == None:
            self.query = 'select * from '+dbname+';'

        self.dbfile = str(os.path.abspath(os.path.expandvars(os.path.expanduser(os.path.normcase(dbname)))))

        self.part = 0
        self.xcon=apsw.Connection(self.dbfile+'.0.db')
        self.xcursor=self.xcon.cursor()
        self.xexec=self.xcursor.execute(self.query)
        return self.xcursor.getdescription()

    def open(self, *parsedArgs, **envars):
        while True:
            try:
                self.xcon.close()
                self.xcon = apsw.Connection(self.dbfile+'.' + str(self.part) + '.db')
                self.xexec = self.xcon.cursor().execute(self.query)
            except Exception,e:
                raise StopIteration

            for row in self.xexec:
                yield row

            self.part += 1

    def close(self):
        self.xcon.close()

def Source():
    return vtiters.SourceCachefreeVT(UnionDB)


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
