# coding: utf-8

import re

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
