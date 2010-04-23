import setpath
import Queue
import functions

from lib.unicodeops import unistr

__docformat__ = 'reStructuredText en'



class condbreak:
    """

    .. function:: condbreak(groupid, C1, C2 ,...., condition, orderby) -> [bgroupid,C1,C2....]

    Returns an expanded *groupid* and the *value1...valueN*, perfoming new groupings when condition is true. Rows grouped together
    are the ones that order by *orderby* column have no intermediate true values for *condition*.

    :Returned multiset schema:
        - *bgroupid*
            *groupid* appended with an integer value indicating the subgroup of the row.
        - *C1, C2 ..*
            The input values of the row.

    .. seealso::

       * :ref:`tutmultiset` functions
    
    >>> table1('''
    ... 1 user1  open
    ... 2 user1  read
    ... 3 user1  close
    ... 4 user1  open
    ... 5 user1  write
    ... 6 user1  close
    ... 7 user2  open
    ... 8 user2  write
    ... ''')
    >>> sql("select condbreak(b,c,c='open',a) from table1 group by b")
    bgroupid | C1
    ----------------
    user11   | open
    user11   | read
    user11   | close
    user12   | open
    user12   | write
    user12   | close
    user21   | open
    user21   | write
    >>> sql("select condbreak(b,c,c='open',a) from (select 4 as a, 6 as b, 9 as c where c!=9)")
    bgroupid | C1
    ---------------
    None     | None

    """
    registered=True
    multiset=True


    def __init__(self):
        self.vals=[]

    def step(self, *args):
        if not args:
            raise functions.OperatorError("condbreak","No arguments")
        if len(args)<4:
            raise functions.OperatorError("condbreak","Wrong number of arguments")
        self.vals.append(list(args))



    def final(self):
        self.vals.sort(key=lambda x:x[-1])
        if self.vals==[]:
            size=0
        else:
            size=len(self.vals[0])-2

        from lib.buffer import CompBuffer
        a=CompBuffer()
        if size<=0:
            a.writeheader(["bgroupid","C1"])
            a.write(["None","None"])
            return a.serialize()
        a.writeheader(["bgroupid"]+["C"+str(i+1) for i in xrange(size-1)])

        counter=0
        for el in self.vals:
            if el[-2]==True:
                counter+=1
            bid=unistr(el[0])+str(counter)
            a.write([bid]+el[1:-2])

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

