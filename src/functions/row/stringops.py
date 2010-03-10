# coding: utf-8
import re
import urllib
import functions
import unicodedata

from lib import chardet

def regexp(*args):

    """
    .. function:: regexp(pattern,expression[,replacestr])

    This function returns a match to the first parenthesis of *pattern*
    or replaces the matches of *pattern* in *expression* with *replacestr*.
    `Pattern Syntax <http://docs.python.org/library/re.html#re-syntax>`_ is
    according python's re module.

    Examples use `inversion`.
    
    Examples:

    >>> table1('''
    ... 25
    ... ''')
    
    >>> sql("regexp 'start\s(\w+)\send' 'start otherword end'  ")
    regexp('start\s(\w+)\send','start otherword end')
    -------------------------------------------------
    otherword

    >>> sql("regexp '\W+' 'nonword' '@#$%@$#% tobereplaced @#$%@#$% ")
    regexp('\W+','nonword','''@#$%@$#% tobereplaced @#$%@#$%')
    ----------------------------------------------------------
    nonwordtobereplacednonword
    """

    if len(args)<2:
        return

    if len(args)==2:
        a=re.search(args[0],args[1],re.UNICODE)
        if a!=None:
            if len(a.groups())>0:
                return a.groups()[0]
            else:
                return True
        else:
            return None

    if len(args)==3:
        return re.sub(args[0],args[1],args[2])

regexp.registered=True

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
        return urllib.unquote_plus(args[0])
    return None
urldecode.registered=True

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
    import lib.Webutils.Funcs as webfuns
    return webfuns.htmlDecode(args[0])
htmldecode.registered=True

def included(*args):
    """
    .. function:: included(str1,str2)

    Returns true if *str1* is included in *str2* or *str2* is included in *str1*.

    .. note::

        If any of the inputs is the *empty string* it returns true.

    Examples:

    >>> sql("select included('Lola start',lower('iStart otherword end')) as test  ")
    test
    ----
    0
    >>> sql("select included('start',lower('iStart lola otherword end')) as test  ")
    test
    ----
    1
    """
    if len(args)!=2:
        raise functions.OperatorError("included","operator takes exactly two arguments")
    if (args[0] in args[1]) or (args[1] in args[0]):
        return True
    return False
included.registered=True

def unitosuni(*args):
    """
    .. function:: unitosuni(str)

    Returns *str* replacing non-ascii characters with their equivalent
    unicode code point literal at the \\u00 format.

    Examples:

    >>> sql("select unitosuni('brûlé') as test  ")
    test
    ---------------
    br\\u00fbl\\u00e9
    >>> sql("select sunitouni(null)")
    sunitouni(null)
    ---------------
    None
    >>> sql("select unitosuni(9)")
    unitosuni(9)
    ------------
    9
    """
    if len(args)!=1:
        raise functions.OperatorError("unitosuni","operator takes only one arguments")
    if args[0]==None:
        return None
    try:
        return repr(unicode(args[0])).replace('\\x','\\u00')[2:-1]
    except Exception:
        return args[0]

unitosuni.registered=True

def sunitouni(*args):
    """
    .. function:: sunitouni(str)

    Returns *str* replacing literal unicode code points to their string representation.

    Examples:

    >>> sql("select sunitouni('br\\u00fbl\\u00e9') as test  ")
    test
    -------
    brûlé
    >>> sql("select sunitouni('\\u that is not a unicode code point') as test  ")
    test
    -----------------------------------
    \u that is not a unicode code point
    >>> sql("select sunitouni(null)")
    sunitouni(null)
    ---------------
    None
    >>> sql("select sunitouni(9)")
    sunitouni(9)
    ------------
    9
    """
    if len(args)!=1:
        raise functions.OperatorError("sunitouni","operator takes only one arguments")
    if args[0]==None:
        return None
    kk="u'%s'" %(unicode(args[0]).replace("'","\\'"))
    try:
        return eval(kk)
    except Exception:
        return args[0]

sunitouni.registered=True

def stripchars(*args):
    """
    .. function:: stripchars(str[,stripchars])

    Returns *str* removing leading and trailing whitespace characters
    or *stripchars* characters if given. Works like python's
    `strip function <http://docs.python.org/library/stdtypes.html#str.strip>`_.


    Examples:

    >>> sql("select stripchars(' initial and final spaces  ') as test  ")
    test
    ------------------------
    initial and final spaces
    >>> sql("select stripchars(' <initial and final spaces>  ',' <>') as test  ")
    test
    ------------------------
    initial and final spaces
    >>> sql("select stripchars(null)")
    stripchars(null)
    ----------------
    None
    """
    if len(args)<1:
        raise functions.OperatorError("stripchars","operator takes at least one arguments")
    if args[0]==None:
        return None
    if len(args)<2:
        return unicode(args[0]).strip()
    return unicode(args[0]).strip(args[1])
stripchars.registered=True

def reencode(*args):
    if len(args)!=1:
        raise functions.OperatorError("reencode","operator takes only one arguments")

    us=args[0]
    if us==None:
        return None
    us=unicode(us)
    try:
        a=unicode(us.encode('iso-8859-1'),'utf-8')
        return a
    except Exception:
        try:
            a=unicode(us.encode('windows-1252'),'utf-8')
            return a
        except Exception:
            return us

reencode.registered=False

def normuni(*args):
    """
    .. function:: normuni(str)

    Returns *str* normalised in the composed unicode normal form without replacing
    same look characters. For example this 'À' character can be encoded with one or two
    different characters, :func:`normuni` returns an one-character encoded version. This
    function is important to check true strings equality.

    Functions :func:`sunitouni` and :func:`unitosuni` are used in the examples to make it more comprehensive.

    Examples:

    .. note::
        Returned results in the next two examples should look the same,
        if not that is a bug at the combined characters rendering of the shell
        that the documentation was created.

    >>> sql("select sunitouni('C\u0327') as test  ")
    test
    ----
    Ç
    >>> sql("select normuni(sunitouni('C\u0327')) as test  ")
    test
    ----
    Ç
    >>> sql("select unitosuni(normuni(sunitouni('C\u0327'))) as test  ")
    test
    ------
    \u00c7
    """
    if len(args)!=1:
        raise functions.OperatorError("normuni","operator takes only one arguments")
    if args[0]==None:
        return None    
    return unicodedata.normalize('NFC', args[0])

normuni.registered=True

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
