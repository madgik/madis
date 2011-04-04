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

    """

    return jlist.toj(args)

jpack.registered=True

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

    fj=[]
    for j in args:
        fj+=[ str(x).replace('\t', '    ') for x in jlist.fromj(j) ]
        
    return '\t'.join(fj)

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
    .. function:: jmerge(jpacks) -> str

    Merges multiple jpacks into one jpack.

    Examples:

    >>> sql("select jmerge('[1,2,3]', '[1,2,3]', 'a', 3 )") # doctest: +NORMALIZE_WHITESPACE
    jmerge('[1,2,3]', '[1,2,3]', 'a', 3 )
    -------------------------------------
    [1, 2, 3, 1, 2, 3, "a", 3]

    """

    fj=[]
    for j in args:
        fj+=jlist.fromj(j)

    return jlist.toj(fj)

jmerge.registered=True

def jset(*args):

    """
    .. function:: jset(jpacks) -> str

    Returns a set representation of a jpack, unifying duplicate items.

    Examples:

    >>> sql("select jset('[1,2,3]', '[1,2,3]', 'b', 'a', 3 )") # doctest: +NORMALIZE_WHITESPACE
    jset('[1,2,3]', '[1,2,3]', 'b', 'a', 3 )
    ----------------------------------------
    [1, 2, 3, "a", "b"]

    """

    fj=[]
    for j in args:
        fj+=jlist.fromj(j)

    return jlist.toj(sorted(set(fj)))

jset.registered=True

def jsort(*args):

    """
    .. function:: jsort(jpacks) -> str

    Sorts the input jpacks.

    Examples:

    >>> sql("select jsort('[1,2,3]', '[1,2,3]', 'b', 'a', 3 )") # doctest: +NORMALIZE_WHITESPACE
    jsort('[1,2,3]', '[1,2,3]', 'b', 'a', 3 )
    -----------------------------------------
    [1, 1, 2, 2, 3, 3, 3, "a", "b"]

    """

    fj=[]
    for j in args:
        fj+=jlist.fromj(j)

    return jlist.toj(sorted(fj))

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

    fj=[]
    for j in args:
        for j1 in jlist.fromj(j):
            b.write([j1])

    return b.serialize()

jsplitv.registered=True
jsplitv.multiset=True


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