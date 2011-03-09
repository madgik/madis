"""
.. function:: oaiget(url, verb, metadataPrefix,...)

    Fetches data from an OAIPMH service, using resumption tokens to fetch large datasets.

:Returned table schema:
    Column C1 as text

Examples:

    >>> sql("select * from oaiget('verb:ListRecords', 'metadataPrefix:ctxo')")    # doctest:+ELLIPSIS
    Traceback (most recent call last):
    ...
    OperatorError: Madis SQLError: operator oaiget: An OAIPMH URL should be provided

    >>> sql("select * from (oaiget verb:ListRecords metadataPrefix:ctxo 'http://oaiurl' )")    # doctest:+ELLIPSIS
    Traceback (most recent call last):
    ...
    OperatorError: Madis SQLError: operator oaiget: <urlopen error [Errno -2] Name or service not known>

"""
import vtiters
import functions

registered=True

class oaiget(vtiters.StaticSchemaVT):
    def getschema(self):
        return [('c1', 'text')]

    def open(self, *parsedArgs, **envars):
        
        def buildURL(baseurl, opts):
            return '?'.join([ baseurl, '&'.join([x+'='+y for x,y in opts if y!=None]) ])

        import urllib2
        import re

        from lib import argsparse
        opts= argsparse.parse(parsedArgs)[1]

        if 'http' not in opts:
            raise functions.OperatorError(__name__.rsplit('.')[-1],"An OAIPMH URL should be provided")

        baseurl='http:'+opts['http']

        del(opts['http'])

        opts=list(opts.iteritems())

        findrestoken=re.compile(r""">([^\s]+?)</resumptionToken>""", re.DOTALL| re.UNICODE)

        resumptionToken=None
        url=buildURL(baseurl, opts+[('resumptionToken', resumptionToken)])

        try:
            while True:
                for i in urllib2.urlopen(url):
                    if resumptionToken==None:
                        t=findrestoken.search(i)
                        if t:
                            resumptionToken=t.groups()[0]
                    yield i.strip()
                if resumptionToken==None:
                    break
                url=buildURL(baseurl, [(x,y) for x,y in opts if x=='verb']+[('resumptionToken', resumptionToken)])
                resumptionToken=None
        except Exception,e:
            raise functions.OperatorError(__name__.rsplit('.')[-1],e)


def Source():
    return vtiters.SourceCachefreeVT(oaiget)


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
