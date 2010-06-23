import setpath
import functions
from lib.buffer import memunpack , mempack
from lib.buffer import CompBuffer
import apsw

def unpackcol(*args):
    """
    .. function:: unpackcol(pack[,colname1,colname2,...]) -> [packd_colname1,packd_colname2,...]
    
    This multiset row function unpacks in columns the vector-like object which is returned by :func:`~functions.aggregate.packing.pack` and :func:`~functions.aggregate.packing.vecpack` functions
    using the key values of the vector object as column headers concatenated with underscore character with the provided *colname1,colname2*. Provided *colnames* must be at least as many as
    the arithmetic values of the pack, except if it is only one where no *colnames* are necessary.
    

    :Returned multiset schema:
        Columns are named by the dimensions of the pack provided.

    .. seealso::

        * :ref:`tutmultiset` functions
        * :ref:`Pivot example <pivoting>`


    Examples:

    >>> table1('''
    ... string1   1 20
    ... string2   1 30
    ... string3   2 40
    ... string4   2 90
    ... ''')
    >>> sql("select unpackcol(pk) from (select pack(a,b) as pk from table1)")
    string4 | string2 | string3 | string1
    -------------------------------------
    2       | 1       | 2       | 1

    Here more than one arithmetic value is included in the pack, so equal number of
    *colname* arguments should be provided.

    >>> sql("select unpackcol(pk)  from (select pack(a,b,c) as pk from table1)")
    Traceback (most recent call last):
    ...
    OperatorError: Madis SQLError: operator unpackcol: To unpack at least 2 tags is needed

    Using :func:`showpack` to view the pack of the previous example.

    >>> sql(\"""select showpack(pk) as spk
    ...             from (select pack(a,b,c) as pk from table1)\""")
    spk
    ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    [ { u ' s t r i n g 4 ' :   [ 2 ,   9 0 ] ,   u ' s t r i n g 2 ' :   [ 1 ,   3 0 ] ,   u ' s t r i n g 3 ' :   [ 2 ,   4 0 ] ,   u ' s t r i n g 1 ' :   [ 1 ,   2 0 ] } ]

    Providing the necessary *colnames* :func:`unpackcol` work correct and the provided names
    are appended with underscore at the column names.

    >>> sql(\"""select unpackcol(pk,'bnum','cnum')
    ...         from (select pack(a,b,c) as pk from table1)\""")
    string4_bnum | string4_cnum | string2_bnum | string2_cnum | string3_bnum | string3_cnum | string1_bnum | string1_cnum
    ---------------------------------------------------------------------------------------------------------------------
    2            | 90           | 1            | 30           | 2            | 40           | 1            | 20

    """

    if len(args)<1:
        raise functions.OperatorError("unpackcol","No arguments")
    pack=args[0]
    mintags=0
    tags=[]
    if len(args)>=2:
        tags=args[1:]
    vec=memunpack(pack)
    a=CompBuffer() # On empty pack??
    row=[]
    for key in vec:
        if hasattr(vec[key],'__iter__'):
            mintags=len(vec[key])
            break
    if len(tags)<mintags:
        raise functions.OperatorError("unpackcol","To unpack at least %s tags is needed" %(str(mintags)))
    elif len(tags)>mintags and len(tags)>1:
        tags=tags[:mintags]

    if len(tags)>0:        
        headers=[key+'_'+tag for key in vec for tag in tags]
    else:
        headers=[key for key in vec]
    a.writeheader(headers)
    if mintags>0:
        row=[el for key in vec for el in vec[key]]
    else:
        row=[vec[key] for key in vec]
    a.write(row)
    return a.serialize()
unpackcol.registered=True
unpackcol.multiset=True

def showpack(*args):
    """
    .. function:: showpack(pack)

    This row function shows a string representation of a *pack*, the system
    vector-like object which is returned by :func:`~functions.aggregate.packing.pack`
    and :func:`~functions.aggregate.packing.vecpack` function.

    Examples:
    
    >>> table1('''
    ... string1   1
    ... string2   1
    ... string3   2
    ... string4   2
    ... ''')
    >>> sql("select showpack(pk) as spk from (select pack(a,b) as pk from table1)")
    spk
    ---------------------------------------------------------------------------------------------------------------------------
    [ { u ' s t r i n g 4 ' :   2 ,   u ' s t r i n g 2 ' :   1 ,   u ' s t r i n g 3 ' :   2 ,   u ' s t r i n g 1 ' :   1 } ]
    >>> sql("select showpack(pk) as spk from (select pack(a) as pk from table1)")
    spk
    ---------------------------------------------------------------------------------------------------------------------------
    [ { u ' s t r i n g 4 ' :   1 ,   u ' s t r i n g 2 ' :   1 ,   u ' s t r i n g 3 ' :   1 ,   u ' s t r i n g 1 ' :   1 } ]
    >>> sql("select showpack(pk) as spk from (select pack('title',a,b,b*b) as pk from table1)")
    spk
    -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    [ { u ' t i t l e . s t r i n g 4 ' :   [ 2 ,   4 ] ,   u ' t i t l e . s t r i n g 1 ' :   [ 1 ,   1 ] ,   u ' t i t l e . s t r i n g 2 ' :   [ 1 ,   1 ] ,   u ' t i t l e . s t r i n g 3 ' :   [ 2 ,   4 ] } ]
    """

    out=[]
    for pack in args:
        out+=[memunpack(pack)]
    return ' '.join(repr(out))

showpack.registered=True

def normalisepack(*args):
    """

    .. function:: normalisepack(pack)

    Returns a normalised version of *pack*. All arithmetic values of a pack should sum to 1.
    *Pack* is the system vector-like object which is returned by :func:`~functions.aggregate.packing.pack`
    and :func:`~functions.aggregate.packing.vecpack` function.

    Function :func:`showpack` is used to view the changes of the *pack*.

    Examples:
     
    >>> table1('''
    ... movie1   4   10
    ... movie2   3   20
    ... movie3   2   50
    ... movie4   1   20
    ... ''')
    >>> sql(\"""select showpack(normalisepack(pk)) as spk
    ...         from (select pack(a,b) as pk from table1)\""")
    spk
    -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    [ { u ' m o v i e 2 ' :   0 . 2 9 9 9 9 9 9 9 9 9 9 9 9 9 9 9 9 ,   u ' m o v i e 3 ' :   0 . 2 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 ,   u ' m o v i e 1 ' :   0 . 4 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 2 ,   u ' m o v i e 4 ' :   0 . 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 } ]
    >>> sql(\"""select showpack(normalisepack(pk)) as spk
    ...         from (select pack(a,b,c) as pk from table1)\""")
    spk
    ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    [ { u ' m o v i e 2 ' :   [ 0 . 2 9 9 9 9 9 9 9 9 9 9 9 9 9 9 9 9 ,   0 . 2 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 ] ,   u ' m o v i e 3 ' :   [ 0 . 2 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 ,   0 . 5 ] ,   u ' m o v i e 1 ' :   [ 0 . 4 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 2 ,   0 . 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 ] ,   u ' m o v i e 4 ' :   [ 0 . 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 ,   0 . 2 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 ] } ]


.. doctest::
    :hide:

    >>> table1('''
    ... movie1   0   10
    ... movie2   0   20
    ... movie3   0   50
    ... movie4   0   20
    ... ''')
    >>> sql(\"""select showpack(pk) as spk
    ...         from (select pack(a,b) as pk from table1)\""")
    spk
    -------
    [ { } ]
    >>> sql(\"""select showpack(normalisepack(pk)) as spk
    ...         from (select pack(a,b) as pk from table1)\""")
    spk
    -------
    [ { } ]
    """
    if len(args)>1:
        raise functions.OperatorError("normalisepack","operator takes only one argument")
    vec=memunpack(args[0])
    listlen=0
    for i in vec:
        if hasattr(vec[i],'__iter__'):
            listlen=len(vec[i])
        break

    if listlen==0:
        sm=float(sum(vec.values()))
        for el in vec:
            vec[el]=float(vec[el])/sm
    else:
        for i in xrange(listlen):
            sm=float(sum([vec[el][i] for el in vec]))
            for el in vec:
                vec[el][i]=float(vec[el][i])/sm
    return mempack(vec)

normalisepack.registered=True

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
