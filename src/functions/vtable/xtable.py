"""
.. function:: xtable()


"""
import vtiters
import functions
import apsw
import re

registered=True

class Xtable(vtiters.SchemaFromArgsVT):
    def __init__(self):
        self.xcursor=None
        self.xcon=None

    def getschema(self, *parsedArgs,**envars):
        opts=self.full_parse(parsedArgs)

        query=None
        tablename=None

        if 'tablename' in opts[1]:
            tablename=opts[1]['tablename']

        if 'table' in opts[1]:
            tablename=opts[1]['table']

        try:
            query=opts[1]['query']
        except:
            pass

        try:
            dbname=opts[0][0]
        except:
            raise functions.OperatorError(__name__.rsplit('.')[-1],"A db filename should be provided")

        if query==None:
            query='select * from '+tablename+';'

        self.xcon=apsw.Connection(dbname)
        self.xcursor=self.xcon.cursor()

        self.xexec=self.xcursor.execute(query)

        return self.xcursor.getdescription()

    def open(self, *parsedArgs, **envars):
        print "opening"

        for row in self.xexec:
            yield row

    def close(self):
        self.xcon.close()

def Source():
    return vtiters.SourceCachefreeVT(Xtable)


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
