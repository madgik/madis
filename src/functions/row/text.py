# coding: utf-8
import re
import functions
import unicodedata

from lib import jlist

# Every regular expression containing \W \w \D \d \b \S \s needs to be compiled
# like below. If you want to embed the UNICODE directive inside the
# regular expression use:
# (?u) like re.sub(ur'(?u)[\W\d]', ' ', o)
delete_numbers_and_non_letters=re.compile(ur'[\W]',re.UNICODE)
delete_non_letters=re.compile(ur'[\W]',re.UNICODE)
delete_word_all=re.compile(ur'\w+\sall',re.UNICODE)
delete_word_all_and_or=re.compile(ur'\w+\sall\s(?:and|or)',re.UNICODE)
reduce_spaces=re.compile(ur'\s+', re.UNICODE)
cqlterms=('title', 'subject', 'person', 'enter', 'creator', 'isbn')

def keywords(*args):

    """
    .. function:: keywords(text1, [text2,...]) -> text

    Returns the keywords inside a single column (text1) or aggregated
    multiple columns.

    Examples:

    >>> table1('''
    ... first(second)   third+fourth
    ... πρωτο(δευτερο)  τριτο+τέταρτο
    ... 'πέμπτο all'      'έκτο title all τεστ'
    ... ''')
    >>> sql("select keywords(a,b) from table1")
    keywords(a,b)
    ---------------------------------------------------
    first second third fourth
    πρωτο δευτερο τριτο τέταρτο
    πέμπτο all έκτο title all τεστ
    """

    out=[]
    for i in args:
        o=i.lower()
        o=delete_numbers_and_non_letters.sub(' ',o)
        o=reduce_spaces.sub(' ',o)
        o=o.strip()
        o=o.split(' ')

        for k in o:
            if len(k)>0:
                out.append(k)

    return ' '.join(out)

keywords.registered=True

def cqlkeywords(*args):

    """
    .. function:: cqlkeywords(text1, [text2,...]) -> text

    Returns the keywords inside a single column (text1) or aggregated
    from multiple columns.

    The difference of cqlkeywords to keywords is that cqlkeywords also
    strips cql syntax like "title all" or "author all" and plain cql directives
    like 'creator', 'title'...

    Examples:

    >>> table1('''
    ... first(second)   third+fourth
    ... πρωτο(δευτερο)  τριτο_τέταρτο
    ... 'πέμπτο all'      'έκτο title all τεστ'
    ... 'title all and something' 'other'
    ... 'title and something' 'other'
    ... ''')
    >>> sql("select cqlkeywords(a,b) from table1")
    cqlkeywords(a,b)
    ---------------------------------------------------
    first second third fourth
    πρωτο δευτερο τριτο_τέταρτο
    έκτο τεστ
    something other
    and something other
    """

    out=[]
    for i in args:
        o=i.lower()
        o=delete_non_letters.sub(' ',o)
        o=delete_word_all_and_or.sub('',o)
        o=delete_word_all.sub('',o)
        o=reduce_spaces.sub(' ',o)
        o=o.strip()
        o=o.split(' ')

        for k in o:
            if len(k)>0 and k not in cqlterms:
                out.append(k)

    return ' '.join(out)

cqlkeywords.registered=True


def kwnum(*args):

    """
    .. function:: kwnum(text1, [text2,...]) -> int

    Returns the number of simple keywords in a string.
    Its input should be words separated by spaces, as returned by
    cqlkeywords or keywords.

    Examples:

    >>> table1('''
    ... 'word1 word2 word3'
    ... 'word1 word2'
    ... 'word'
    ... ''')
    >>> sql("select kwnum(a) from table1")
    kwnum(a)
    --------
    3
    2
    1
    """

    o=0
    for i in args:
        o+=len(i.split(' '))

    return o

kwnum.registered=True

def uniqueterms(*args):
    """
    .. function:: uniqueterms(text1, [text2,...]) -> text

    Returns the unique terms of an input string.

    Examples:

    >>> table1('''
    ... 'word1 word2 word2'
    ... 'word1 word2 word1'
    ... 'word'
    ... ''')
    >>> sql("select uniqueterms(a) from table1")
    uniqueterms(a)
    --------------
    word1 word2
    word1 word2
    word
    """

    o=set()
    l=[]
    for i in args:
        for t in i.split(' '):
            if t not in o and not t=='':
                o.add(t)
                l.append(t)

    return ' '.join(l)

uniqueterms.registered=True


match_field_all=re.compile('(title|isbn|issn|subject|creator|language|type)\sall',re.UNICODE)

def cqlfields(*args):

    """
    This functions returns the keywords inside a single column or aggregated
    from multiple columns. It plays well with Unicode.

    The difference of cqlkeywords to keywords is that cqlkeywords also
    strips cql syntax like "title all" or "author all".

    >>> table1('''
    ... '(title all "scrieri") and (creator all "arghezi") and (title all "other")'
    ... '("maschinenschreiben") and (language all "ger")'
    ... '("sauer") and ("übungsbuch")'
    ... ''')
    >>> sql("select cqlfields(a) from table1")
    cqlfields(a)
    -------------------
    title creator title
    language
    <BLANKLINE>
    """

    out=[]
    for i in args:
        o=i.lower()
        o=delete_numbers_and_non_letters.sub(' ',o)
        fields=match_field_all.findall(o)

        for k in fields:
            out.append(k)
    return ' '.join(out)


cqlfields.registered=True

def comprspaces(*args):
    """
    .. function:: comprspaces(text1, [text2,...]) -> text

    This function strips (from the beginning and the end) and compresses
    the spaces in its input.

    Examples:

    >>> table1('''
    ... '   an example    with spaces      '    'another    example with spaces         '
    ... ''')
    >>> sql("select comprspaces(a,b) from table1")
    comprspaces(a,b)
    --------------------------------------------------
    an example with spaces another example with spaces
    """

    out=[]
    for i in args:
        o=i.strip()
        o=reduce_spaces.sub(' ',o)
        out+=[o]

    return ' '.join(out)

comprspaces.registered=True


# Every regular expression containing \W \w \D \d \b \S \s needs to be compiled
# like below. If you want to embed the UNICODE directive inside the
# regular expression use:
# (?u) like re.sub(ur'(?u)[\W\d]', ' ', o)
query_regular_characters=re.compile(ur"""^[("„”“‘’´«»’ʹ–\w\s\[!-~\]]*$""", re.UNICODE)

def isvalidutf8(*args):

    """
    .. function:: isvalidutf8(text) -> 1/0

    Returns 1 if the input text is in valid UTF-8 format, or 0 if not.
    This function is used to find corrupted UTF-8 strings with a heuristic
    based on non common characters.

    Examples:

    >>> table1('''
    ... test
    ... δοκιμή!
    ... sÃ©vignÃ
    ... Ã©vezred
    ... ''')
    >>> sql("select isvalidutf8(a) from table1")
    isvalidutf8(a)
    --------------
    1
    1
    0
    0
    """

    for i in args:
        if i==None:
            return 0
        if not query_regular_characters.match(i):
            return 0

    return 1

isvalidutf8.registered=True

def regexpr(*args):

    """
    .. function:: regexp(pattern,expression[,replacestr])

    This function returns a match to the first parenthesis of *pattern*
    or replaces the matches of *pattern* in *expression* with *replacestr*.
    `Pattern Syntax <http://docs.python.org/library/re.html#re-syntax>`_ is
    according to python's re module.

    Examples use `inversion`.
    
    Examples:

    >>> table1('''
    ... 25
    ... ''')
    
    >>> sql("regexpr 'start\s(\w+)\send' 'start otherword end'  ")
    regexpr('start\s(\w+)\send','start otherword end')
    --------------------------------------------------
    otherword

    >>> sql("regexpr '\W+' 'nonword' '@#$%@$#% tobereplaced @#$%@#$%' ")
    regexpr('\W+','nonword','@#$%@$#% tobereplaced @#$%@#$%')
    ---------------------------------------------------------
    nonwordtobereplacednonword
    """
    if len(args)<2:
        return

    if len(args)==2:
        a=re.search(args[0], unicode(args[1]),re.UNICODE)
        if a!=None:
            if len(a.groups())>0:
                return jlist.toj(a.groups())
            else:
                return True
        else:
            return None

    if len(args)==3:
        return re.sub(args[0],args[1],args[2])

regexpr.registered=True

def regexprmatches(*args):

    """
    .. function:: regexprmatches(pattern, arg)

    This function returns true if the pattern matches arg or false otherwise.

    Examples use `inversion`.

    Examples:

    >>> sql("regexprmatches '(a)' 'qwer a qwer'  ")
    regexprmatches('(a)','qwer a qwer')
    -----------------------------------
    1

    """
    if len(args)!=2:
        raise functions.OperatorError('regexprmatches', 'Two parameters should be provided')

    a=re.search(args[0], unicode(args[1]),re.UNICODE)
    if a!=None:
        return True
    else:
        return None

regexprmatches.registered=True



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
