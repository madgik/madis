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
import urllib2
import vtiters
from lib import TableHTMLParser



registered=True
external_stream=True




class WebTable(vtiters.InitBySampleVT):
    def parse(self,*args):
        tableNum=1
        argsnum=len(args)
        if argsnum<1 or argsnum>2:
            raise functions.OperatorError(__name__.rsplit('.')[-1],"Wrong number of arguments")
        tableUrl=args[0]
        if argsnum==2:
            try:
                tableNum=int(args[1])
            except Exception:
                raise functions.OperatorError(__name__.rsplit('.')[-1],"Table number ot extract must be integer")
        return (tableUrl, tableNum)

    def getschema(self,samplerow):
        if 'tuple' in str(type(samplerow)):
            return [(header,'text') for header in samplerow]
        else:
            return [('C'+str(i),'text') for i in range(1, len(samplerow)+1)]
        
    def open(self,tableUrl, tableNum,**envars):
        return TableParse(tableUrl, tableNum)



class TableParse:
    def __init__(self,tableUrl, tableNum):
        url = tableUrl

        try:
            txdata = None
            txheaders = {
                'User-Agent': 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)',
            }
            req = urllib2.Request(url, txdata, txheaders)
            self.ufile = urllib2.urlopen(req)
            headers = self.ufile.info()
        except Exception:
            raise functions.OperatorError(__name__.rsplit('.')[-1],"Cannot load url:'%s'" %(str(url)))
        parser = TableHTMLParser.TableHTMLParser(tableNum)
        
        self.iterator=linkiter(self.ufile,parser.parse)
    def __iter__(self):
        return self
    def next(self):
        try:
            current = self.iterator.next()
            return current
        except TableHTMLParser.HTMLParseError,e:            
            raise functions.OperatorError(__name__.rsplit('.')[-1],e)

        
    def close(self):
        self.ufile.close()
        

def linkiter(source,consume):
    for inp in source:
        for out in consume(inp):
                yield out



def Source():
    return vtiters.SourceCachefreeVT(WebTable)


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
        