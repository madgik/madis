# coding: utf-8
import urlparse
import os
import mimetypes
from lib.buffer import CompBuffer

def urlsplit(*args):

    """
    .. function:: urlsplit(text1, [text2,...]) -> multiset

    Breaks a given URL into multiple fields. The returned table schema is:

    :scheme: What type the URL is (e.g. http, ftp ...)
    :netloc: Network location of URL (e.g. www.text.com)
    :path: Path part of URL (e.g. /data/2010/). It always has a slash at the end
    :filename: Filename part of URL
    :type: Mime type of URL, or if not a mime type exists, the extension part of filename.
    :subtype: Mime subtype of URL.
    :params: All parameters following ';' in URL.
    :query: All parameters following '?' in URL.
    :fragment: All parameters following '#' in URL.

    Examples:

    >>> table1('''
    ... http://www.test.com/apath/bpath/fname.pdf
    ... http://www.test.com/search.csv;p=5?q=test#hl=en
    ... ''')
    >>> sql("select urlsplit(a) from table1")
    scheme | netloc       | path          | filename   | type        | subtype | params | query  | fragment
    -------------------------------------------------------------------------------------------------------
    http   | www.test.com | /apath/bpath/ | fname.pdf  | application | pdf     |        |        |
    http   | www.test.com | /             | search.csv | csv         |         | p=5    | q=test | hl=en
    """

    c=CompBuffer()

    c.writeheader(['scheme', 'netloc', 'path', 'filename', 'type', 'subtype', 'params', 'query', 'fragment'])

    url=''.join(args)
    u=urlparse.urlparse(''.join(args))
    pf=os.path.split(u[2])

    if len(pf)==2:
        path, filename=pf
    else:
        path, filename=pf[0], ''

    if len(path)>0 and path[-1]!='/':
        path+='/'

    m=mimetypes.guess_type(url)
    if m[0]!=None:
        m1, m2=m[0].split('/')
    else:
        m1, m2=(os.path.splitext(filename)[1], '')
        if len(m1)>0 and m1[0]=='.':
            m1=m1[1:]

    c.write([u[0], u[1], path, filename, m1, m2, u[3], u[4], u[5]])
    return c.serialize()

urlsplit.registered=True
urlsplit.multiset=True

def urllocation(*args):

    """
    .. function:: urllocation(str) -> str

    Returns the location part of provided URL.

    Examples:

    >>> table1('''
    ... http://www.test.com/apath/bpath/fname.pdf
    ... http://www.test.com/search.csv;p=5?q=test#hl=en
    ... ''')
    >>> sql("select urllocation(a) from table1")
    urllocation(a)
    -----------------------------------------
    http://www.test.com/apath/bpath/fname.pdf
    http://www.test.com/search.csv
    """
    
    u=urlparse.urlparse(''.join(args))

    return u[0]+u'://'+''.join(u[1:3])

urllocation.registered=True

def fileextension(*args):

    """
    .. function:: fileextension(text) -> text

    Returns the extension of a given text argument.

    Examples:

    >>> table1('''
    ... "http://www.test.com/lalala.gif"
    ... "http://www.test.com/lalala.GIF"
    ... ''')
    >>> sql("select fileextension(a) from table1")
    fileextension(a)
    ----------------
    .gif
    .gif

    """

    try:
        ret=os.path.splitext(args[0])
    except ValueError:
        return None

    return ret[1].lower()

fileextension.registered=True

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
