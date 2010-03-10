__docformat__ = 'reStructuredText en'
import setpath
import functions
from lib.buffer import CompBuffer , mempack , memunpack




class mergebypriority:
    """

    .. function:: mergebypriority(pack,priority) -> [dimension,rank]

    Returns a ranking of group *pack* dimensions, based on higher *priority* pack value for
    that dimension. Different input packs cannot have the same priority.

    :Returned multiset schema:
        - *dimension*
            Input *pack* group dimensions
        - *rank*
            Integer value 1,...n, indicating dimension's rank. Top ranking is value 1.


    .. seealso::
    
        * :func:`~functions.aggregate.packing.pack`, :func:`~functions.aggregate.packing.vecpack`
        * :ref:`tutmultiset` functions

    .. note::

        Do not use packs from vecpack or in general packs that could include zeros because if the
        higher priority pack has zero, dimensions with zero values will be placed higher because of priority.
    
    Examples:
    
    >>> table1('''
    ... personal   movie1 20
    ... personal   movie2 30
    ... national   movie1 1000
    ... national   movie2 100
    ... national   movie3 500
    ... aggregate  movie1 1000
    ... aggregate   movie2 800
    ... aggregate   movie3 1200
    ... aggregate   movie4 10000
    ... ''')

    >>> table2('''
    ... personal   3
    ... national   2
    ... aggregate   1
    ... ''')
    >>> sql(\"""select mergebypriority(pk,priorities.b)
                    from
                        (select a,pack(b,c) as pk from table1 group by a) as profile,
                        table2 as priorities
                    where priorities.a=profile.a\""")
    dimension | rank
    ----------------
    movie2    | 1
    movie1    | 2
    movie3    | 3
    movie4    | 4

.. doctest::
    :hide:
        
    >>> table3('''
    ... personal   movie1 lo 20 3
    ... personal   movie2 la 30 1
    ... national   movie1 lq 1000 1
    ... national   movie2 lo 100 5
    ... national   movie3 po 500 5
    ... aggregate  movie1 io 1000 90
    ... aggregate   movie2 op 800 45
    ... aggregate   movie3 so 1200 23
    ... aggregate   movie4 lo 10000 234
    ... ''')
    >>> sql("select mergebypriority(pk,priorities.b) from (select a,pack(b,c,d) as pk from table3 group by a) as profile, table2 as priorities where priorities.a=profile.a")
    dimension | rank
    ----------------
    movie2.la | 1
    movie1.lo | 2
    movie1.lq | 3
    movie3.po | 4
    movie2.lo | 5
    movie4.lo | 6
    movie3.so | 7
    movie1.io | 8
    movie2.op | 9
    >>> sql("select mergebypriority(pk) from (select 5 as pk,2 as a where pk!=5)")
    dimension | rank
    ----------------
    None      | None
    
    .. notreallytrue
        There is not need for :func:`~functions.vtable.setschema.setschema` in aggregate :ref:`tutmultiset` operator in empty
        resultset in from field changed all aggregate return null in empty, with (group by null) they
        do not return anything .. so setschema will be needed anyway.


    """

    registered=True 
    multiset=True

    def __init__(self):
        self.first=True
        self.packslist=[]


    def step(self, *args):
        if self.first:
            if len(args)<2:
                raise functions.OperatorError("mergebypriority","Two values required pack and priority")            
            self.first=False
        self.packslist.append((args[1],args[0]))


    def final(self):
        self.packslist.sort(reverse=True)
        pkmerged=[]
        spkmerged=set(pkmerged)
        for priority, pk in self.packslist:
            pr=memunpack(pk)
            spr=set(pr.iterkeys())
            extravals=sorted([(pr[key],key) for key in list(spr-spkmerged)],reverse=True)
            for i in extravals:
                pkmerged.append(i[1]) #continue ranking from current profile
            spkmerged=set(pkmerged)
        from lib.buffer import CompBuffer
        a=CompBuffer()
        a.writeheader(["dimension","rank"])
        if pkmerged==[]:
            a.write(["None","None"])

        i=0
        for el in pkmerged:
            a.write([el,i+1])
            i+=1

        return a.serialize()


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


