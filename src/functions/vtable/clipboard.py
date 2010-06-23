"""
.. function:: webtable(query:None[,defaulttype[,column:type]])

    Returns the result of the input *query* casting types according to *column:type* pairs and cast rest of the columns to optional *defaulttype*.

:Returned table schema:
    Column names same as input query, types as defined in parameters.

Examples:

    >>> sql("select * from webtable('http://en.wikipedia.org/wiki/List_of_countries_by_public_debt') limit 3")
    Rank | Country               | % of GDP[1] | Date
    ------------------------------------------------------
    1    | Zimbabwe              | 304.30      | 2009 est.
    2    | Japan                 | 192.10      | 2009 est.
    3    | Saint Kitts and Nevis | 185.00      | 2009 est.

"""
import setpath

import functions
import vtiters

registered=True
external_stream=True

class clipboard(vtiters.InitBySampleVT):
    def __init__(self):
        self.schema=['C1']

    def getschema(self,samplerow):
        return self.schema

    def open(self, **envars):
        import lib.clip as clip
        data=clip.getcbtext().split('\n')

        hasschema=True
        count=0
        if len(data)>0:
            count=data[0].count('\t')+1
            for i in data[1:]:
                if i.count('\t')+1!=count:
                    hasschema=False
                    break

        if hasschema:
            self.schema=[('C'+str(i),'text') for i in xrange(1,count+1)]
            data=[i.split('\t') for i in data]
        else:
            data=[[r] for r in data]

        return iter(data)

def Source():
    return vtiters.SourceCachefreeVT(clipboard)


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
