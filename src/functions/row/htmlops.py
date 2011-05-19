# coding: utf-8
import urllib
import re
from htmlentitydefs import name2codepoint
name2codepoint['#39'] = 39

def htmlunescape(s):
    return re.sub('&(%s);' % '|'.join(name2codepoint),
              lambda m: unichr(name2codepoint[m.group(1)]), s)

def htmldecode(*args):
    """
    .. function:: htmldecode(str)

    Returns the html decoded *str*.

    Examples:

    >>> sql("select htmldecode('(&quot;die+wunderbaren+jahre&quot;)') as query")
    query
    -------------------------
    ("die+wunderbaren+jahre")
    >>> sql("select htmldecode(null) as query")
    query
    -----
    None
    """
    if len(args)>1:
        raise functions.OperatorError("htmldecode","operator takes only one argument")
    if args[0]==None:
        return None
    return htmlunescape(args[0])

htmldecode.registered=True

def urldecode(*args):
    """
    .. function:: urldecode(str)

    Returns the url decoded *str*.

    Examples:

    >>> sql("select urldecode('where%2Ccollid%3Dcolid+and+u%3D%27val%27') as query")
    query
    ------------------------------
    where,collid=colid and u='val'


    >>> sql("select urldecode(null) as query")
    query
    -----
    None
    """
    if len(args)>1:
        raise functions.OperatorError("urldecode","operator takes only one argument")
    if args[0]!=None:
        return unicode(urllib.unquote_plus(args[0]))
    return None

urldecode.registered=True

def urlencode(*args):
    """
    .. function:: urlescape(str)

    Returns the escaped URL.

    Examples:

    >>> sql("select urlencode('where, collid=colid') as query")
    query
    -----------------------
    where%2C+collid%3Dcolid

    """
    if len(args)>1:
        raise functions.OperatorError("urlencode","operator takes only one argument")
    if args[0]!=None:
        return urllib.quote_plus(unicode(args[0]))
    return None

urlencode.registered=True

def url(*args):
    """
    .. function:: url(href, linktext)

    Returns the a url pointing to *href* and having the link text *linktext*.

    Examples:

    >>> sql("select url('http://somewhere.org') as url")
    url
    -------------------------------------------------------
    <a href="http://somewhere.org">http://somewhere.org</a>

    >>> sql("select url('somewhere.org') as url")
    url
    ------------------------------------------------
    <a href="http://somewhere.org">somewhere.org</a>

    >>> sql("select url('somewhere.org', 'go somewhere') as url")
    url
    -----------------------------------------------
    <a href="http://somewhere.org">go somewhere</a>

    """
    def addhttp(u):
        if u.find('://')==-1:
            return u'http://'+unicode(u)
        return unicode(u)

    if len(args)>2:
        raise functions.OperatorError("url","operator a maximum of two arguments")

    if len(args)==2:    
        if args[1]!=None:
            return '<a href="'+addhttp(args[0])+'">'+unicode(args[1])+'</a>'

    if args[0]==None:
        return None
    return '<a href="'+addhttp(args[0])+'">'+unicode(args[0])+'</a>'

url.registered=True

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
