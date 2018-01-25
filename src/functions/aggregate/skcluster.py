import setpath
import functions
import math
import numpy as np
import time as t
# import re
import json
# from collections import deque

class skcluster:
    """
    .. function:: skcluster(str,rowid cols)

        :NOTE:

            The present operator requires the following packages: 'numpy', 'scipy', 'sklearn'
            numpy & scipy: https://www.scipy.org/scipylib/download.html
            sklearn: http://scikit-learn.org/stable/install.html

        Implements the clustering algorithm initialized by str and returns the sample id, the coordinates in space and its
        cluster label. Cols refer to features except for the first one which includes each dato id.
        In case the algorithm computes centroids in clusters, #features more columns are returned: The coordinates of
        cluster centroids in which the dato belongs to. For instance, if dataset consists of 4 columns (= 4 features)
        4 more columns will be added in result table in case centroids have been computed

        Parameters:

        :initstr:

                Initialization string of the algorithm with optional parameters (from scikit-learn api, ie: KMeans(n_clusters=3)).

        :cols:
                Names of the input-variables


        Examples:
        A dataset with 3 columns (1 column for the id and 2 features):

        >>> table1('''
        ... 0.52   0.40
        ... 0.63   0.33
        ... 0.77   0.15
        ... 0.81   0.74
        ... ''')

        >>> sql("select skcluster('AffinityPropagation()',c1,c2) from table1")
        ---------------------------
        id | label | center1 | center2
        --------------
        1 | 0 | 0.63 | 0.33
        2 | 0 | 0.63 | 0.33
        3 | 0 | 0.63 | 0.33
        4 | 1 | 0.81 | 0.74

        In case algorithm doesn't compute centroids, only the 'id' and 'label' columns appeared in result

        >>> sql("select skcluster('SpectralClustering(n_clusters=2)',c1,c2) from table1")
        ---------------------------
        id | label
        --------------
        1 | 0 |
        2 | 0 |
        3 | 0 |
        4 | 1 |

    """


    registered = True  # Value to define db operator

    def __init__(self):
        # self.init = True
        self.sample = []
        # self.id=[]
        self.values=[]
        self.start=t.time()
        self.sampleID = 0



    def initargs(self, args):
        from sklearn.neighbors import kneighbors_graph
        from sklearn.cluster import *
        # self.initkm = KMeans(init='k-means++', n_clusters=2, n_init=10)

        if not args:
            raise functions.OperatorError("Clustering", "No data")
        elif len(args)<3:
            raise functions.OperatorError("Wrong number of arguments (missing values)")
        else:
            self.initalg = eval(args[0])

    def step(self, *args):
        # if self.init == True:
        self.sampleID +=1
        self.initargs(args)

        #Creating the dataset
        temprow=[]
        values=args[1:]

        for c in values:
            try:
                temprow.append(round(float(c),2))
            except ValueError:
                raise functions.OperatorError(c,"wrong type of argument")

        # print 'sample:',temprow
        self.sample.append(temprow)

    def final(self):


        ids = [i+1 for i,x in enumerate(self.sample)]
        # data = self.sample
        # print data
        alg = self.initalg.fit(self.sample)
        print 'Num of features:',len(self.sample[0])
        if hasattr(alg,'cluster_centers_'):
            print alg.cluster_centers_
            yield tuple(['id','label'] + ['center'+str(i) for i in xrange(1,len(self.sample[0])+1)])
            for id in ids:
                # label=int(alg.labels_[id-1])
                yield [id] + [int(alg.labels_[id-1])] + list(alg.cluster_centers_[int(alg.labels_[id-1])])

        else:
            yield tuple(['id','label'])
            for id in ids:
                yield [id, int(alg.labels_[id-1])]
