"""
.. function: skpredict(args,query:None)

skpredict filename: "mymodel" select * from t;

    Loads a predictive model trained by sktrain operator from file (stored from sktrain operator) and classifies the new
    data provided selected from the query. It returns a table with the new predictions


    >>> table1(''' (Last column = response variable (classes or conitunous value in case of regression))
    ... 5.1	3.5	1.4	0.2	1
    ... 4.9	3	1.4	0.2	1
    ... 4.7	3.2	1.3	0.2	2
    ... 4.6	3.1	1.5	0.2	2
    ... 5	3.6	1.4	0.2	0
    ... 5.4	3.9	1.7	0.4	1
    ... 4.6	3.4	1.4	0.3	1
    ... 5	3.4	1.5	0.2	0
    ... 4.4	2.9	1.4	0.2	0
    ... 4.9	3.1	1.5	0.1	2
    ... 5.4	3.7	1.5	0.2	2
    ... 4.8	3.4	1.6	0.2	1
    ... --- [0|Column names ---
    ... [1|C1 [2|C2 [3|C3 [4|C4 [5|C5
    ... ''')

    sql("skpredict filename:SVMmodel")
    skpredict filename:SVMmodel select C1,C2,C4 from table;

    ------------------------------

"""



__author__ = 'root'
# import os.path
# import sys
# import setpath
# from vtout import SourceNtoOne
# import functions
# import lib.inoutparsing
import setpath
import vtbase
import functions
import gc
import lib.inoutparsing

registered = True

class skpredict(vtbase.VT):
    def VTiter(self, *parsedArgs,**envars):
        import itertools
        # from sklearn import linear_model
        import cPickle as cp
        import zlib

        largs, dictargs = self.full_parse(parsedArgs)

        if 'query' not in dictargs:
            raise functions.OperatorError(__name__.rsplit('.')[-1],"No query argument ")
        query = dictargs['query']

        cur = envars['db'].cursor()
        c = cur.execute(query, parse=False)
        schema = []
        try:
            schema = [x[0] for x in cur.getdescriptionsafe()]
        except StopIteration:
            try:
                raise
            finally:
                try:
                    c.close()
                except:
                    pass

        if 'filename' not in dictargs:
            raise functions.OperatorError(__name__.rsplit('.')[-1],"No filename provided")
        f = open(dictargs['filename'],'r')
        # Load model
        fdecomp = zlib.decompress(f.read()) # Decompression
        model = cp.loads(fdecomp) # Deserialization
        yield [('prediction',)]
        for i in c:
            # print int(model.predict(i)[0])
            yield [int(model.predict(i)[0])]



def Source():
    return vtbase.VTGenerator(orf_skpredict)

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
