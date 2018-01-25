"""
.. function: skpredict(args,query:None)



skpredict filename: "mymodel" select * from t;

    Loads a predictive model trained by sktrain operator from file (stored from sktrain operator) and classifies the new
    data provided selected from the query. It returns a table with the new predictions


    >>> table('''
    ... 0.0   4.4   0
    ... 2.1   2.2   2
    ... -2.1   4.4   0
    ... 2.1   2.2   0
    ... 0.0   4.4   2
    ... -4.2   4.4   2
    ... -4.2   4.4   1
    ... -2.1   -0.0   0
    ... 2.1   -0.0   0
    ... -2.1   -2.2   0
    ... -4.2   -0.0   2
    ... --- [0|Column names ---
    ... [1|C1 [2|C2 [3|C3
    ... ''')
    >>> sql("skpredict filename:SVMmodel select C1,C2 from table;")
    id  |  prediction  |  prediction_probability_per_class
    -------------
    0   |  0           |  [ 0.4101318   0.20131647  0.38855173]
    1   |  0           |  [ 0.41863251  0.20180877  0.37955871]
    2   |  2           |  [ 0.27520722  0.19621797  0.52857481]
    3   |  0           |  [ 0.4149133   0.20182841  0.3832583 ]
    4   |  0           |  [ 0.4101318   0.20131647  0.38855173]
    5   |  2           |  [ 0.90338454  0.01203995  0.08457551]
    6   |  2           |  [ 0.90338454  0.01203995  0.08457551]
    7   |  0           |  [ 0.27481114  0.19661277  0.52857609]
    8   |  0           |  [ 0.27504844  0.19632018  0.52863138]
    9   |  0           |  [ 0.27491203  0.19661313  0.52847484]
    10  |  2           |  [ 0.77210661  0.12397848  0.10391491]

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
        import numpy as np
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
        if hasattr(model,'predict_proba'):
            yield [('id'), ('prediction',),('prediction_probability_per_class'),]
            # yield [('id'), ('prediction',),]
            for i,row in enumerate(c):
                # print np.reshape(i,(1,-1)),type(i)
                prob = model.predict_proba(np.reshape(list(row), (1, -1)))[0]
                yield (i, int(model.predict(np.reshape(list(row), (1, -1)))[0]), str(prob))

        else:
            # print 'no prob',
            yield [('id'), ('prediction',),]
            for i,row in enumerate(c):
                # print 'sample format:', list(row)
                yield (i, int(model.predict(np.reshape(list(row),(1,-1)))[0]))



def Source():
    return vtbase.VTGenerator(skpredict)

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
