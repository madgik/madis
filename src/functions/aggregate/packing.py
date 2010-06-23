__docformat__ = 'reStructuredText en'
import setpath
import functions
from lib.buffer import CompBuffer , mempack , memunpack

class vecpack:
    """

    .. function:: vecpack(dpack,dimension1,dimension2,.... [,value1, value2,...])

    Works like :func:`pack` taking additionally the parameter *dpack* that is a pack of
    the dimensions that input should be packed. This dimensions will be included in the
    returned pack even if no input lines include them. The values that are pack with these
    dimensions is zero (or a list of 0s depending on the number of numerical values).
    Only values appearing in *dpack* are allowed in the aggregating rows *dimension1,dimension2..*

    .. note::
        
        :func:`vecpack` should be preffered from :func:`pack` when it is important that every pack of a group in query
        should have the same dimensions. For example to pivot a table with :func:`~functions.row.managepacks.unpackcol`, packs should have the same dimensions.

    
    To view a string representation of the returned object the examples below use :func:`~functions.row.managepacks.showpack` row function.

    Examples:
    
    >>> table1('''
    ... a   string   5
    ... a   num      4
    ... b   num      3
    ... c   string   9
    ... ''')
    
    Using :func:`pack` function to pack columns b and c grouping by a, the resulting packs include only dimensions (dictionary keys / column b values)
    that exist in the group. So packs are not uniform with each other, eg. In the example below value *a* of fcol has a pack with dimensions *num* and *string* while
    the other two have only one of the dimensions.
    
    >>> sql("select a as fcol,showpack(pack(b,c)) as vpk from table1 group by a")
    fcol | vpk
    ------------------------------------------------------------
    a    | [ { u ' n u m ' :   4 ,   u ' s t r i n g ' :   5 } ]
    b    | [ { u ' n u m ' :   3 } ]
    c    | [ { u ' s t r i n g ' :   9 } ]
    
    Using vecpack instead of pack the resulting packs will have the same dimensions, the ones given as first argument of vecpack. So
    statement *select pack(distinct b) as pk from table1* serves to form the dimensions pack (*num* and *string*) to be given as
    first input of vecpack.
    
    >>> sql("select a as fcol,showpack(vecpack(pk,b,c)) as vpk from table1, (select pack(distinct b) as pk from table1) group by a")
    fcol | vpk
    ------------------------------------------------------------
    a    | [ { u ' n u m ' :   4 ,   u ' s t r i n g ' :   5 } ]
    b    | [ { u ' n u m ' :   3 ,   u ' s t r i n g ' :   0 } ]
    c    | [ { u ' n u m ' :   0 ,   u ' s t r i n g ' :   9 } ]
    """


    registered=True #Value to define db operator

    def __init__(self):
        self.valuesdict=dict()
        self.first=True
        self.num=-1




    def step(self, *args):
        valen=1
        if self.first:
            if len(args)<1:
                raise functions.OperatorError("vecpack","Operator needs at list the dimensions argument")
            packet=args[0]
        args=args[1:]
        if self.first:            
            self.num=len(args)
            for i in xrange(len(args)):
                if not args[i]:
                    raise functions.OperatorError("vecpack","Cannot pack null values")
                try:
                    float(args[i])
                    self.num=i
                    break
                except ValueError:
                    continue
        valuestr='.'.join([args[i].replace('.','') for i in xrange(self.num)])
        if self.num==len(args): ### no arithmetic values
            value=1
        elif len(args)-self.num>1: ###many numeric values , return list
            value=[args[i] for i in xrange(self.num,len(args))]
            valen=len(args)-self.num
        else:
            value=args[self.num]
        if self.first:
            self.first=False
            try:
                self.valuesdict=memunpack(packet)
                for el in self.valuesdict:
                    if valen>1:
                        self.emptyval=valen*[0]
                    else:
                        self.emptyval=0
                    self.valuesdict[el]=self.emptyval
            except Exception:
                raise functions.OperatorError("vecpack"," Incorrect first argument format")
        if valuestr not in self.valuesdict:
            raise functions.OperatorError("vecpack"," Dimension %s was not included in initialization set" %(valuestr))
        if self.valuesdict[valuestr]!=self.emptyval:
            raise functions.OperatorError("vecpack"," Dimension %s found twice" %(valuestr))
        self.valuesdict[valuestr]=value

    def final(self):
        return mempack(self.valuesdict)



class pack:
    """

    .. function:: pack(dimension1,dimension2,.... [,value1, value2, ...])
    
    Returns a *blob* object that packs string values (*dimension1,dimension2,....*)
    along with potential numerical values [*value1, value2 ...*] in a compressed python dictionary.
    String values are concatenated using the dot character as delimiter between them.
    Numerical values are appended so as to form a list of numbers.

    Concatenated string values constitue the keys in the generated compressed python dictionary (hence they must be unique)
    and concatenated numerical values form the dictionary's values. When no numerical values
    are provided, the dictionary's values are all set to 1.
    
    .. note::

        This function provides the means for keeping many columns and rows of table groups into a single value.
        This is especially useful and powerful when combined with row functions such as :func:`~functions.row.managepacks.unpackcol` or :func:`~functions.row.similarity.cosine` to perform action as pivot and similarity calculation.

    The following examples use :func:`~functions.row.managepacks.showpack` row function in order to view a string representation of the returned object.

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

    registered=True #Value to define db operator

    def __init__(self):
        self.valuesdict=dict()
        self.first=True
        self.num=-1


    def step(self, *args):
        if self.first:
            self.num=len(args)
            for i in xrange(len(args)):
                if args[i]==None:
                    raise functions.OperatorError("pack","Cannot pack null values")
                try:
                    float(args[i])
                    self.num=i
                    break
                except ValueError:
                    continue
        valuestr='.'.join([args[i].replace('.','') for i in xrange(self.num)])
        if self.num==len(args):
            value=1
        elif len(args)-self.num>1: ###many numeric values , return list
            value=[args[i] for i in xrange(self.num,len(args))]
        else:
            value=args[self.num]
        if valuestr in self.valuesdict:
            raise functions.OperatorError("pack","Dimension %s found twice" %(valuestr))
        if value!=0:
            self.valuesdict[valuestr]=value

    def final(self):
        return mempack(self.valuesdict)


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
