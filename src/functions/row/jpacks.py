import lib.jopts as jopts
import json
import operator
import itertools
try:
    from collections import OrderedDict
except ImportError:
    # Python 2.6
    from lib.collections import OrderedDict

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
    ["a","b",3]

    >>> sql("select jpack('a', jpack('b',3))")
    jpack('a', jpack('b',3))
    ------------------------
    ["a",["b",3]]

    """

    return jopts.toj(jopts.elemfromj(*args))

jpack.registered=True

def jsonstrict(*args):

    """
    .. function:: jsonstrict(args...) -> json string

    Sometimes we wish to process json lists from another application. Jsonstrict function
    tries to always create json compatible lists. So it always returns json lists.

    Examples:

    >>> sql("select jsonstrict('a')")
    jsonstrict('a')
    ---------------
    ["a"]

    >>> sql("select jsonstrict('a','b',3)")
    jsonstrict('a','b',3)
    ---------------------
    ["a","b",3]

    >>> sql("select jsonstrict('a', jpack('b',3))")
    jsonstrict('a', jpack('b',3))
    -----------------------------
    ["a",["b",3]]

    """

    return json.dumps(jopts.elemfromj(*args), separators=(',',':'), ensure_ascii=False)

jsonstrict.registered=True

def jlen(*args):

    """
    .. function:: jlen(args...) -> int

    Returns the total length in elements of the input jpacks.

    Examples:

    >>> sql("select jlen('abc')")
    jlen('abc')
    -----------
    1

    >>> sql("select jlen('a','b',3)")
    jlen('a','b',3)
    ---------------
    3

    >>> sql("select jlen('a', jpack('b',3))")
    jlen('a', jpack('b',3))
    -----------------------
    3

    >>> sql("select jlen('[1,2,3]')")
    jlen('[1,2,3]')
    ---------------
    3

    """
    return sum([len(x) if type(x) in (dict,list) else 1 for x in (jopts.elemfromj(*args))])

jlen.registered=True

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
    ["a",3]

    >>> sql("select jfilterempty('[3]', jpack('b', ''))")
    jfilterempty('[3]', jpack('b', ''))
    -----------------------------------
    [3,"b"]

    """

    return jopts.toj([x for x in jopts.fromj(*args) if x!='' and x!=[] and x!=None])

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

    return '\t'.join([ str(x).replace('\t', '    ') for x in jopts.fromj(*args) ])

j2t.registered=True

def t2j(*args):

    """
    .. function:: t2j(tabpack) -> jpack

    Converts a tab separated pack to a jpack.

    Examples:

    >>> sql("select t2j(j2t('[1,2,3]'))") # doctest: +NORMALIZE_WHITESPACE
    t2j(j2t('[1,2,3]'))
    -------------------
    ["1","2","3"]

    """
    
    fj=[]
    for t in args:
        fj+=t.split('\t')

    return jopts.toj(fj)

t2j.registered=True

def jmerge(*args):

    """
    .. function:: jmerge(jpacks) -> jpack

    Merges multiple jpacks into one jpack.

    Examples:

    >>> sql("select jmerge('[1,2,3]', '[1,2,3]', 'a', 3 )") # doctest: +NORMALIZE_WHITESPACE
    jmerge('[1,2,3]', '[1,2,3]', 'a', 3 )
    -------------------------------------
    [1,2,3,1,2,3,"a",3]

    """

    return jopts.toj( jopts.fromj(*args) )

jmerge.registered=True

def jset(*args):

    """
    .. function:: jset(jpacks) -> jpack

    Returns a set representation of a jpack, unifying duplicate items.

    Examples:

    >>> sql("select jset('[1,2,3]', '[1,2,3]', 'b', 'a', 3 )") # doctest: +NORMALIZE_WHITESPACE
    jset('[1,2,3]', '[1,2,3]', 'b', 'a', 3 )
    ----------------------------------------
    [1,2,3,"a","b"]

    """

    return jopts.toj(sorted(set( jopts.fromj(*args) )))

jset.registered=True

def jsort(*args):

    """
    .. function:: jsort(jpacks) -> jpack

    Sorts the input jpacks.

    Examples:

    >>> sql("select jsort('[1,2,3]', '[1,2,3]', 'b', 'a', 3 )") # doctest: +NORMALIZE_WHITESPACE
    jsort('[1,2,3]', '[1,2,3]', 'b', 'a', 3 )
    -----------------------------------------
    [1,1,2,2,3,3,3,"a","b"]

    """

    return jopts.toj(sorted( jopts.fromj(*args) ))

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

    yield ('C1', )

    for j1 in jopts.fromj(*args):
        yield [jopts.toj(j1)]

jsplitv.registered=True

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

    fj=[jopts.toj(x) for x in jopts.fromj(*args)]

    if fj==[]:
        yield ('C1',)
            
    yield tuple( ['C'+str(x) for x in xrange(1,len(fj)+1)] )
    yield fj

jsplit.registered=True

def jflatten(*args):

    """
    .. function:: jflattten(jpacks) -> jpack

    Flattens all nested sub-jpacks.

    Examples:

    >>> sql(''' select jflatten('1', '[2]') ''') # doctest: +NORMALIZE_WHITESPACE
    jflatten('1', '[2]')
    --------------------
    ["1",2]

    >>> sql(''' select jflatten('[["word1", 1], ["word2", 1], [["word3", 2], ["word4", 2]], 3]') ''') # doctest: +NORMALIZE_WHITESPACE
    jflatten('[["word1", 1], ["word2", 1], [["word3", 2], ["word4", 2]], 3]')
    -------------------------------------------------------------------------
    ["word1",1,"word2",1,"word3",2,"word4",2,3]

    """

    return jopts.toj( jopts.flatten( jopts.elemfromj(*args) ))

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

    return '|'.join('(?:'+x+')' for x in jopts.fromj(*args))

jmergeregexp.registered=True

def jdictkeys(*args):

    """
    .. function:: jdictkeys(jdict) -> jpack

    Returns a jpack of the keys of input jdict

    Examples:

    >>> sql(''' select jdictkeys('{"k1":1,"k2":2}', '{"k1":1,"k3":2}') ''') # doctest: +NORMALIZE_WHITESPACE
    jdictkeys('{"k1":1,"k2":2}', '{"k1":1,"k3":2}')
    -----------------------------------------------
    ["k1","k2","k3"]

    >>> sql(''' select jdictkeys('{"k1":1,"k2":2}') ''') # doctest: +NORMALIZE_WHITESPACE
    jdictkeys('{"k1":1,"k2":2}')
    ----------------------------
    ["k1","k2"]
    >>> sql(''' select jdictkeys('test') ''') # doctest: +NORMALIZE_WHITESPACE
    jdictkeys('test')
    -----------------
    []
    >>> sql(''' select jdictkeys(1) ''') # doctest: +NORMALIZE_WHITESPACE
    jdictkeys(1)
    ------------
    []

    """
    
    if len(args)==1:
        keys=[]
        i=args[0]
        try:
            if i[0]=='{' and i[-1]=='}':
                keys=[x for x in json.loads(i, object_pairs_hook=OrderedDict).iterkeys()]
        except TypeError,e:
            pass
    else:
        keys=OrderedDict()
        for i in args:
            try:
                if i[0]=='{' and i[-1]=='}':
                    keys.update([(x,None) for x in json.loads(i, object_pairs_hook=OrderedDict).iterkeys()])
            except TypeError,e:
                pass
        keys=list(keys)
    return jopts.toj( keys )

jdictkeys.registered=True

def jdictvals(*args):

    """
    .. function:: jdictvals(jdict, [key1, key2,..]) -> jpack

    If only the first argument (jdict) is provided, it returns a jpack of the values of input jdict (sorted by the jdict keys).

    If key values are also provided, it returns only the keys that have been provided.

    Examples:

    >>> sql(''' select jdictvals('{"k1":1,"k2":2}') ''') # doctest: +NORMALIZE_WHITESPACE
    jdictvals('{"k1":1,"k2":2}')
    ----------------------------
    [1,2]

    >>> sql(''' select jdictvals('{"k1":1,"k2":2, "k3":3}', 'k3', 'k1', 'k4') ''') # doctest: +NORMALIZE_WHITESPACE
    jdictvals('{"k1":1,"k2":2, "k3":3}', 'k3', 'k1', 'k4')
    ------------------------------------------------------
    [3,1,null]
    >>> sql(''' select jdictvals('{"k1":1}') ''') # doctest: +NORMALIZE_WHITESPACE
    jdictvals('{"k1":1}')
    ---------------------
    1
    >>> sql(''' select jdictvals('{"k1":1}') ''') # doctest: +NORMALIZE_WHITESPACE
    jdictvals('{"k1":1}')
    ---------------------
    1
    >>> sql(''' select jdictvals(1) ''') # doctest: +NORMALIZE_WHITESPACE
    jdictvals(1)
    ------------
    1

    """

    if type(args[0]) in (int,float) or args[0][0]!='{' or args[0][-1]!='}':
        return args[0]
    d=json.loads(args[0])
    if len(args)==1:
        d=d.items()
        d.sort(key=operator.itemgetter(1,0))
        vals=[x[1] for x in d]
    else:
        vals=[]
        for i in args[1:]:
            try:
                vals.append(d[i])
            except KeyboardInterrupt:
                raise
            except:
                vals.append(None)
        
    return jopts.toj( vals )

jdictvals.registered=True

def jdictsplit(*args):

    """
    .. function:: jdictvals(jdict, [key1, key2,..]) -> columns

    If only the first argument (jdict) is provided, it returns a row containing the values of input jdict (sorted by the jdict keys).

    If key values are also provided, it returns only the columns of which the keys have been provided.

    Examples:

    >>> sql(''' select jdictsplit('{"k1":1,"k2":2}') ''') # doctest: +NORMALIZE_WHITESPACE
    k1 | k2
    -------
    1  | 2

    >>> sql(''' select jdictsplit('{"k1":1,"k2":2, "k3":3}', 'k3', 'k1', 'k4') ''') # doctest: +NORMALIZE_WHITESPACE
    k3 | k1 | k4
    --------------
    3  | 1  | None

    """

    d=json.loads(args[0])
    if len(args)==1:
        d=d.items()
        d.sort(key=operator.itemgetter(1,0))
        yield tuple([x[0] for x in d])
        yield [jopts.toj(x[1]) for x in d]
    else:
        vals=[]
        yield tuple(args[1:])
        for i in args[1:]:
            try:
                vals.append(jopts.toj(d[i]))
            except KeyboardInterrupt:
                raise    
            except:
                vals.append(None)
        yield vals

jdictsplit.registered=True

def jsplice(*args):

    """
    .. function:: jsplice(jpack, range1_start, range1_end, ...) -> jpack

    Splices input jpack. If only a single range argument is provided, it returns input jpack's element in provided position. If defined position
    index is positive, then it starts counting from the beginning of input jpack. If defined position is negative it starts counting from the
    end of input jpack.

    If more than one range arguments are provided, then the arguments are assumed to be provided in pairs (start, end) that define ranges inside
    the input jpack that should be joined together in output jpack.

    Examples:

    >>> sql(''' select jsplice('[1,2,3,4,5]',0) ''') # doctest: +NORMALIZE_WHITESPACE
    jsplice('[1,2,3,4,5]',0)
    ------------------------
    1

    >>> sql(''' select jsplice('[1,2,3,4,5]',-1) ''') # doctest: +NORMALIZE_WHITESPACE
    jsplice('[1,2,3,4,5]',-1)
    -------------------------
    5

    >>> sql(''' select jsplice('[1,2,3,4,5]',10) ''') # doctest: +NORMALIZE_WHITESPACE
    jsplice('[1,2,3,4,5]',10)
    -------------------------
    None

    >>> sql(''' select jsplice('[1,2,3,4,5]', 0, 3, 0, 2) ''') # doctest: +NORMALIZE_WHITESPACE
    jsplice('[1,2,3,4,5]', 0, 3, 0, 2)
    ----------------------------------
    [1,2,3,1,2]

    >>> sql(''' select jsplice('[1,2,3,4,5]', 2, -1) ''') # doctest: +NORMALIZE_WHITESPACE
    jsplice('[1,2,3,4,5]', 2, -1)
    -----------------------------
    [3,4]

    """

    largs=len(args)
    if largs==1:
        return args[0]

    fj=jopts.fromj(args[0])

    if largs==2:
        try:
            return jopts.toj(fj[args[1]])
        except KeyboardInterrupt:
            raise
        except:
            return None

    outj=[]
    for i in xrange(1,largs,2):
        try:
            outj+=fj[args[i]:args[i+1]]
        except KeyboardInterrupt:
            raise           
        except:
            pass

    return jopts.toj(outj)
        

jsplice.registered=True

def jcombinations(*args):

    """
    .. function:: jcombinations(jpack, r) -> multiset

    Returns all length r combinations of jpack.

    Examples:

    >>> sql('''select jcombinations('["t1","t2","t3"]',2)''')
    C1 | C2
    -------
    t1 | t2
    t1 | t3
    t2 | t3

    >>> sql('''select jcombinations('["t1","t2",["t3","t4"]]',2)''')
    C1 | C2
    ----------------
    t1 | t2
    t1 | ["t3","t4"]
    t2 | ["t3","t4"]

    >>> sql('''select jcombinations(null,2)''')

    >>> sql('''select jcombinations('["t1","t2","t3","t4"]')''')
    C1
    --
    t1
    t2
    t3
    t4
    """

    r=1
    if len(args)==2:
        r=args[1]

    yield tuple(('C'+str(x) for x in xrange(1,r+1)))
    for p in itertools.combinations(jopts.fromj(args[0]), r):
        yield [jopts.toj(x) for x in p]

jcombinations.registered=True

def jpermutations(*args):

    """
    .. function:: jpermutations(jpack, r) -> multiset

    Returns all length r permutations of jpack.

    Examples:

    >>> sql('''select jpermutations('["t1","t2","t3"]',2)''')
    C1 | C2
    -------
    t1 | t2
    t1 | t3
    t2 | t1
    t2 | t3
    t3 | t1
    t3 | t2

    >>> sql('''select jpermutations('["t1","t2",["t3","t4"]]',2)''')
    C1          | C2
    -------------------------
    t1          | t2
    t1          | ["t3","t4"]
    t2          | t1
    t2          | ["t3","t4"]
    ["t3","t4"] | t1
    ["t3","t4"] | t2

    >>> sql('''select jpermutations(null,2)''')

    >>> sql('''select jpermutations('["t1","t2","t3","t4"]')''')
    C1
    --
    t1
    t2
    t3
    t4
    """

    r=1
    if len(args)==2:
        r=args[1]

    yield tuple(('C'+str(x) for x in xrange(1,r+1)))
    for p in itertools.permutations(jopts.fromj(args[0]), r):
        yield [jopts.toj(x) for x in p]

jpermutations.registered=True


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