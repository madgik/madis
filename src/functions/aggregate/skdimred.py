import setpath
import functions
import math
import numpy as np
import time as t
# import re
import json

from sklearn.decomposition import *
from sklearn.preprocessing import StandardScaler
# from sklearn.cluster import * # for FeatureAgglomeration.
from sklearn.manifold import *
from collections import deque




class skdimred:

    """
    .. function:: skdimred(initstr,cols)

        Implements dimensionality reduction on table t (based on algorithms from Machine Learning package scikit-learn.org).
        Returns: the transformed data in the new space.
        initstr: Initialization string of the algorithm (3 methods are supported: PCA, SVD and TSNE)
        cols: Names of the input-variables

        Examples:
        Sample from the iris dataset with 4 columns (SepalLength, SepalWidth, PetalLength, PetalWidth):

        >>> table1('''
        ... 5.1	3.5	1.4	0.2
        ... 4.9	3	1.4	0.2
        ... 4.7	3.2	1.3	0.2
        ... 4.6	3.1	1.5	0.2
        ... 5	3.6	1.4	0.2
        ... ''')

        >>> sql("select skdimred('PCA(n_components=2)',SepalLength,SepalWidth,PetalLength,PetalWidth) from table1;")

        ------------------------------

    """
    registered = True  # Value to define db operator

    def __init__(self):

        # self.init = True
        self.sample = []
        self.id=[]
        self.values=[]
        self.initcounter = 0
        self.start=t.time()
        # self.initkm = KMeans(init='k-means++', n_clusters=2, n_init=10)


    def initargs(self, args):
        if not args:
            raise functions.OperatorError("Polynomial Interpolation:", "No data")
        elif len(args)<4:
            raise functions.OperatorError("Wrong number of arguments (missing values)")


    def step(self, *args):
        # if self.init == True:
        self.initargs(args)

        #Initialization of the model:
        if self.initcounter==0:
            # self.str=args[0]
            self.initalg = eval(args[0])
            self.initcounter+=1

        #Creating the dataset:
        temprow=[]
        values=args[1:]


        for c in values:
            try:
                temprow.append(round(float(c),2))
            except ValueError:
                raise functions.OperatorError(c,"wrong type of argument")

        self.sample.append(temprow)


    def final(self):
        data = self.sample
        scaler = StandardScaler()
        data_scaled = scaler.fit_transform(data)
        Xr = self.initalg.fit_transform(data_scaled)
        # Xr = self.initalg.fit_transform(data)
        try:
            print 'EXPLAINED VARIANCE (madis):',self.initalg.explained_variance_ratio_
        except:
            pass

        yield tuple(['eig'+str(i+1) for i in range(len(Xr[0]))])
        for val in Xr:
            yield val

