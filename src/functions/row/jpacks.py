import lib.jlist as jlist
from lib.buffer import CompBuffer,emptyBuffer

def jpack(*args):

    """
    .. function:: jpack(args...) -> jpack

    Converts multiple input arguments into a single string. Jpacks preserve the types
    of their inputs and are based on JSON encoding. Single values are represented as
    themselves where possible.

    Examples:

    >>> sql("select jpack('a')")
    jpack('a')
    ----------
    a

    >>> sql("select jpack('a','b',3)")
    jpack('a','b',3)
    ----------------
    ["a", "b", 3]

    >>> sql("select jpack('a', jpack('b',3))")
    jpack('a', jpack('b',3))
    ------------------------
    ["a", ["b", 3]]

    """

    return jlist.toj(jlist.elemfromj(*args))

jpack.registered=True

def jfilterempty(*args):
    """
    .. function:: jfilterempty(jpacks.) -> jpack

    Removes from input jpacks all empty elements.

    Examples:

    >>> sql("select jfilterempty('a', '', '[]')")
    jfilterempty('a', '', '[]')
    ---------------------------
    a

    >>> sql("select jfilterempty('a','[null]',3)")
    jfilterempty('a','[null]',3)
    ----------------------------
    ["a", 3]

    >>> sql("select jfilterempty('[3]', jpack('b', ''))")
    jfilterempty('[3]', jpack('b', ''))
    -----------------------------------
    [[3], ["b", ""]]

    """

    return jlist.toj([x for x in jlist.elemfromj(*args) if x!='' and x!=[] and x!=[None]])

jfilterempty.registered=True

def j2t(*args):

    """
    .. function:: j2t(jpack) -> tabpack

    Converts multiple input jpacks to a tab separated pack (tab separated values). If tab characters are found in
    the source jpack

    Examples:

    >>> sql("select j2t('[1,2,3]')") # doctest: +NORMALIZE_WHITESPACE
    j2t('[1,2,3]')
    --------------
    1        2        3

    >>> sql("select j2t('[1,2,3]','a')") # doctest: +NORMALIZE_WHITESPACE
    j2t('[1,2,3]','a')
    ------------------
    1        2        3        a

    >>> sql("select j2t('a', 'b')") # doctest: +NORMALIZE_WHITESPACE
    j2t('a', 'b')
    -------------
    a        b

    """

    return '\t'.join([ str(x).replace('\t', '    ') for x in jlist.fromj(*args) ])

j2t.registered=True

def t2j(*args):

    """
    .. function:: t2j(tabpack) -> jpack

    Converts a tab separated pack to a jpack.

    Examples:

    >>> sql("select t2j(j2t('[1,2,3]'))") # doctest: +NORMALIZE_WHITESPACE
    t2j(j2t('[1,2,3]'))
    -------------------
    ["1", "2", "3"]

    """
    
    fj=[]
    for t in args:
        fj+=t.split('\t')

    return jlist.toj(fj)

t2j.registered=True

def jmerge(*args):

    """
    .. function:: jmerge(jpacks) -> jpack

    Merges multiple jpacks into one jpack.

    Examples:

    >>> sql("select jmerge('[1,2,3]', '[1,2,3]', 'a', 3 )") # doctest: +NORMALIZE_WHITESPACE
    jmerge('[1,2,3]', '[1,2,3]', 'a', 3 )
    -------------------------------------
    [1, 2, 3, 1, 2, 3, "a", 3]

    """

    return jlist.toj( jlist.fromj(*args) )

jmerge.registered=True

def jset(*args):

    """
    .. function:: jset(jpacks) -> jpack

    Returns a set representation of a jpack, unifying duplicate items.

    Examples:

    >>> sql("select jset('[1,2,3]', '[1,2,3]', 'b', 'a', 3 )") # doctest: +NORMALIZE_WHITESPACE
    jset('[1,2,3]', '[1,2,3]', 'b', 'a', 3 )
    ----------------------------------------
    [1, 2, 3, "a", "b"]

    """

    return jlist.toj(sorted(set( jlist.fromj(*args) )))

jset.registered=True

def jsort(*args):

    """
    .. function:: jsort(jpacks) -> jpack

    Sorts the input jpacks.

    Examples:

    >>> sql("select jsort('[1,2,3]', '[1,2,3]', 'b', 'a', 3 )") # doctest: +NORMALIZE_WHITESPACE
    jsort('[1,2,3]', '[1,2,3]', 'b', 'a', 3 )
    -----------------------------------------
    [1, 1, 2, 2, 3, 3, 3, "a", "b"]

    """

    return jlist.toj(sorted( jlist.fromj(*args) ))

jsort.registered=True

def jsplitv(*args):

    """
    .. function:: jsplitv(jpacks) -> [C1]

    Splits vertically a jpack.

    Examples:

    >>> sql("select jsplitv(jmerge('[1,2,3]', '[1,2,3]', 'b', 'a', 3 ))") # doctest: +NORMALIZE_WHITESPACE
    C1
    --
    1
    2
    3
    1
    2
    3
    b
    a
    3

    """

    b=CompBuffer()
    b.writeheader(['C1'])

    for j1 in jlist.fromj(*args):
        b.write([j1])

    return b.serialize()

jsplitv.registered=True
jsplitv.multiset=True

def jsplit(*args):

    """
    .. function:: jsplit(jpacks) -> [C1, C2, ...]

    Splits horizontally a jpack.

    Examples:

    >>> sql("select jsplit('[1,2,3]', '[3,4,5]')") # doctest: +NORMALIZE_WHITESPACE
    C1 | C2 | C3 | C4 | C5 | C6
    ---------------------------
    1  | 2  | 3  | 3  | 4  | 5

    """

    b=CompBuffer()
    
    fj=jlist.fromj(*args)

    if fj==[]:
        return emptyBuffer('C1')
            
    b.writeheader( ['C'+str(x+1) for x in xrange(len(fj))] )
    b.write(fj)

    return b.serialize()

jsplit.registered=True
jsplit.multiset=True

def jflatten(*args):

    """
    .. function:: jflattten(jpacks) -> jpack

    Flattens all nested sub-jpacks.

    Examples:

    >>> sql(''' select jflatten('1', '[2]') ''') # doctest: +NORMALIZE_WHITESPACE
    jflatten('1', '[2]')
    --------------------
    ["1", 2]

    >>> sql(''' select jflatten('[["word1", 1], ["word2", 1], [["word3", 2], ["word4", 2]], 3]') ''') # doctest: +NORMALIZE_WHITESPACE
    jflatten('[["word1", 1], ["word2", 1], [["word3", 2], ["word4", 2]], 3]')
    -------------------------------------------------------------------------
    ["word1", 1, "word2", 1, "word3", 2, "word4", 2, 3]

    """

    return jlist.toj( jlist.flatten( jlist.elemfromj(*args) ))

jflatten.registered=True

def jmergeregexp(*args):

    """
    .. function:: jmergeregexp(jpacks) -> jpack

    Flattens all nested sub-jpacks.

    Examples:

    >>> sql(''' select jmergeregexp('["abc", "def"]') ''') # doctest: +NORMALIZE_WHITESPACE
    jmergeregexp('["abc", "def"]')
    ------------------------------
    (?:abc)|(?:def)

    """

    return '|'.join('(?:'+x+')' for x in jlist.fromj(*args))

jmergeregexp.registered=True


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