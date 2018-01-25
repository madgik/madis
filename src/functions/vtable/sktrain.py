"""
.. function: sktrain(args,query:None)

    :NOTE:

        The operator requires the following packages: 'numpy', 'scipy', 'sklearn'
        numpy & scipy: https://www.scipy.org/scipylib/download.html
        sklearn: http://scikit-learn.org/stable/install.html


    Fits data from specific database relations into cross-validated predictive models. A supervised algorithm initialized
    by initstr is trained on the selected data and returns its predictions for each sample (either for Regression or
    Classification problems). The algorithm implements the validation step via cross-validation and extra parameters
    for the training can be provided as well. The model is also stored in disk for future use. (see skpredict operator)

    Returns: a table schema with the model's classification (predicted labels). In case user inserts the initstr parameter
    "probability=True", the table consists of two more columns: the probability of each prediction and one list with the
    probabilities for each sample to belong to each class (useful for evaluation metrics, ie: ROC curves).

    Parameters:

    :initstr(with optional parameters):

        Initialization string (from scikit-learn api, ie: DecisionTreeClassifier(max_depth=3)

    :classname:

        The Column name for the response variable we want to classify/predict

    :cv:

        k for k-fold cross validation


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

    >>> sql("sktrain filename:SVMmodel initstr:SVC(kernel='linear') classname:C3 cv:10 select * from table;")
    sktrain filename:SVMmodel initstr:SVC(kernel='linear') cv:10 select * from table;  //10-fold cross-validation

    id |  predicted_label |  prediction_probability  |  probs_per_class
    ------------------------------------------------------------------------------------------------------------------
    0  | 2                |  0.0                     |  [0.0, 0.0, 0.0]
    1  | 0                |  0.0                     |  [0.0, 0.0, 0.0]
    2  | 2                |  0.0                     |  [0.0, 0.0, 0.0]
    3  | 0                |  0.410210360487          |  [0.41021036048685278, 0.14907264577206564, 0.44071699374108164]
    4  | 0                |  0.548051122534          |  [0.54805112253403776, 0.14785556444024275, 0.30409331302571929]
    5  | 1                |  0.193336225736          |  [0.38875643772373958, 0.19333622573639794, 0.4179073365398624]
    6  | 2                |  0.0                     |  [0.0, 0.0, 0.0]
    7  | 0                |  0.416031694023          |  [0.41603169402299173, 0.18204494673933225, 0.40192335923767586]
    8  | 0                |  0.448463699747          |  [0.44846369974736427, 0.1393806568854721, 0.41215564336716359]
    9  | 2                |  0.216144116096          |  [0.61342034424348868, 0.17043553966069536, 0.21614411609581588]
    10 | 0                |  0.52171544466           |  [0.52171544465978703, 0.20100090883455271, 0.27728364650566051]


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

class sktrain(vtbase.VT):
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
                    del trainList[i][idgroupname]
                else:
                    groups=None

            X = np.array(trainList).astype(np.float)
            y = np.array(targetList).astype(np.int)

            preds = []
            pred_probs = []
            # print 'MADIS/GROUPS?: ',groups
            preds = cross_val_predict(model, X, y, cv=cv, groups=groups)
                # pred_probs = cross_val_predict(model, X, y, cv=cv_func,method='predict_proba')
            # if model.probability:
            if hasattr(model, 'probability') and model.probability:
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
            if hasattr(model,'probability') and model.probability:
            # if model.probability:
                yield [('id',), ('predicted_label',), ('prediction_probability',),('probs_per_class',)]
                for i in range(len(X)):
                    pred = preds[i]
                    yield (i, int(pred), pred_probs[i][pred], str([pred_probs[i][j] for j in range(len(model.classes_))]))
                    # yield (i, int(pred), pred_probs[i][pred], [pred_probs[i][j] for j in range(len(model.classes_))])
            else:
                yield [('id',), ('predicted_label',),]
                for i in range(len(X)):
                    pred = preds[i]
                    yield (i, int(pred))


def Source():
    return vtbase.VTGenerator(sktrain)



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