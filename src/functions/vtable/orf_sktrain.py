"""
sktrain using yield

    Implements the supervised algorithm initialized by initstr and fits the data ("training") provided by table t.
    User chooses the response variable (classname attribute) and the k for k-fold cross validation (cv attribute).
    If no cv is provided, a defauld 5-fold cross-validation is applied.
    Operator returns the predictions for each sample(either for Regression or Classification problems)

    Examples:

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

    sql("orf_sktrain classname:C3 initstr:SVC(kernel='linear') cv:10") //10-fold cross-validation
    sktrain filename:SVMmodel initstr:SVC(kernel='linear') cv:10 select * from table;
    
    NOTE about cross-validation on classification/regression tasks:
    For integer/None inputs, if the estimator is a classifier and y is either binary or multiclass, StratifiedKFold() is used.
    Otherwise (like regression tasks), KFold() is used.
    Stratified cross-validation: Each set contains approximately the same percentage of samples of each target class as the complete set. Thus,
    it is ensured that relative class frequencies is approximately preserved in each train and validation fold.    
    
    ------------------------------

"""
import sklearn

registered = True
__author__ = 'root'
import os.path
import sys
from vtout import SourceNtoOne


import setpath
import vtbase
import functions
import gc
import lib.inoutparsing

class orf_sktrain(vtbase.VT):
    def VTiter(self, *parsedArgs,**envars):

        largs, dictargs = self.full_parse(parsedArgs)

        if 'query' not in dictargs:
            raise functions.OperatorError(__name__.rsplit('.')[-1],"No query argument ")
        query = dictargs['query']
        print 'MADIS/QUERY', query
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
        f = open(dictargs['filename'],'w')

        if 'initstr' not in dictargs:
            raise functions.OperatorError(__name__.rsplit('.')[-1],"No initialization string")
        initstr = dictargs['initstr']
        #-- IMPORT MODULES ---
        import itertools
        from sklearn.cluster import *
        from sklearn.linear_model import *
        from sklearn.neighbors import *
        from sklearn.svm import *
        from sklearn.naive_bayes import *
        from sklearn.tree import *
        from sklearn.ensemble import *
        # from sklearn.cross_validation import *
        print 'MADIS/sklearn version', sklearn.__version__
        from sklearn.model_selection import *
        # from sklearn.cluster import AgglomerativeClustering
        import cPickle as cp
        import numpy as np
        # import unicodedata
        import zlib
        # --------------------
        model = eval(initstr)
        print 'MADIS/MODEL:',model
        if 'classname' not in dictargs:
            # raise functions.OperatorError(__name__.rsplit('.')[-1],"No classname argument ")
            trainList=[]
            for row in c:
                trainList=[row for row in c]
            train = np.array(trainList).astype(np.float)

            model.fit(train)
            pstr = cp.dumps(model,2)
            f.write(zlib.compress(pstr,3))
            yield [('id',), ('cluster_label',)]
            for i in xrange(0, len(train)):
                yield (i, int(model.labels_[i]))

        else:
            classname = dictargs['classname']
            idclassname = schema.index(classname)

            trainList = []
            targetList = []
            cv_func = ''
            cv = 0
            if 'cv' not in dictargs:
                cv = 5
            else:
                cv = int(dictargs['cv'])

            #Constructing group of samples:

            if 'groupname' in dictargs:
                groupname = ''
                groups = []
                groupname = dictargs['groupname']
                idgroupname = schema.index(groupname)
                groupList = []
                # print 'trainlist:', trainList

            for i,row in enumerate(c):
                trainList.append(list(row[0:idclassname] + row[idclassname + 1:len(row)]))
                targetList.append(int(row[idclassname]))
                if 'groupname' in dictargs:
                    groupList.append(row[idgroupname])
                    groups = np.array(groupList)
                    # print trainList[i]
                    del trainList[i][idgroupname]
                    # print 'groups:\n', set(groups)
                    # print 'grouping variable: ', groupname
                    # print 'number of groups: ', len(set(groups))
                else:
                    groups=None

            X = np.array(trainList).astype(np.float)
            y = np.array(targetList).astype(np.int)
            # print 'MADIS/TRAIN X: ',X
            # print 'MADIS/TARGET y: ',y
            # if 'groupname' in dictargs:
            #     gkf = GroupKFold(n_splits=cv)
            #     cv_func = gkf.split(X, y, groups)
            #
            # else:
            #     skf = StratifiedKFold(n_splits=cv)
            #     cv_func = skf.split(X, y)


            preds = []
            pred_probs = []
            # preds = cross_val_predict(model, X, y, cv=cv_func)
            print 'MADIS/GROUPS?: ',groups
            preds = cross_val_predict(model, X, y, cv=cv, groups=groups)
                # pred_probs = cross_val_predict(model, X, y, cv=cv_func,method='predict_proba')
            pred_probs = cross_val_predict(model, X, y, cv=cv, groups=groups, method='predict_proba')

            # print 'MADIS/preds',preds
            # print 'MADIS/probs',pred_probs

            #Fit again and Store model in disk:
            model.fit(X,y)
            # pred_probs = model.predict_proba(X)
            pstr = cp.dumps(model,2)
            f.write(zlib.compress(pstr,3))
            # print 'MADIS/CLASSNAMES',model.classes_
            # yield tuple(['id','predicted_label'] + ['center'+str(i) for i in xrange(1,len(self.sample[0])+1)])
            # yield [('id',), ('predicted_label',), ('prediction_probability',),([tuple('probability_'+str(i)+',') for i in range(len(model.classes_))])]
            yield [('id',), ('predicted_label',), ('prediction_probability',),('probs_per_class',)]

            for i in range(len(X)):
                pred = preds[i]
                yield (i, int(pred), pred_probs[i][pred], str([pred_probs[i][j] for j in range(len(model.classes_))]))
                # yield (i, int(pred), pred_probs[i][pred], [pred_probs[i][j] for j in range(len(model.classes_))])


def Source():
    return vtbase.VTGenerator(orf_sktrain)



# def outdata(diter, schema, connection, *args, **formatArgs):
#     # -- IMPORT MODULES ---
#     import itertools
#     from sklearn.linear_model import *
#     from sklearn.neighbors import *
#     from sklearn.svm import *
#     from sklearn.naive_bayes import *
#     from sklearn.tree import *
#     from sklearn.ensemble import *
#     # from sklearn.cluster import AgglomerativeClustering
#     import cPickle as cp
#     import numpy as np
#     # import unicodedata
#     import zlib
#     # ---------------------
#
#     f = open(formatArgs['filename'], 'w')
#
#     # Make rows -> cols
#     gen = itertools.izip(*diter)
#
#     #Split data into train and target sets:
#     train = itertools.islice(gen,0,len(schema)-1)
#     target = itertools.islice(gen,0,1)
#
#     # Reverse again
#     train = np.array(list(itertools.izip(*train))).astype(np.float)
#     target = np.array(list(itertools.chain(*(itertools.izip(*target))))).astype(np.float) #target1 has 2 dimensions. Scikit expects 1: i.chain(reversed vector)
#
#     # Model initialization and training
#     initalg = eval(formatArgs['initstr']) #initialize model
#
#     alg = initalg.fit(train,target) #fit model to data
#     pstr = cp.dumps(alg, 2) # Serialization
#     f.write(zlib.compress(pstr,3)) # Compression
#
#     f.close()
#     f1 = open(formatArgs['filename'], 'r')
#     fedecomp=zlib.decompress(f1.read())
#     model = cp.loads(fedecomp)
#     fimp=model.feature_importances_
#     #print fimp
#     yield ['colname','val']
#
#
#
# boolargs = lib.inoutparsing.boolargs
#
#
# def Source():
#     global boolargs, nonstringargs
#     return SourceNtoOne(outdata, boolargs, lib.inoutparsing.nonstringargs, lib.inoutparsing.needsescape,
#                         connectionhandler=True)



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