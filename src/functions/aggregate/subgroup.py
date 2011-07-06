import setpath
import Queue
import functions
from lib import iso8601
from operator import itemgetter

from lib.unicodeops import unistr

__docformat__ = 'reStructuredText en'


def timedelta2millisec(tdelta):
    return tdelta.days*24*60*60*1000+tdelta.seconds*1000+tdelta.microseconds/1000

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


class datediffbreak:
    """

    .. function:: datediffbreak(groupid, C1, C2 ,...., date, maxdiff[,'order',orderbycol1,orderbycol2,...]) -> [bgroupid,C1,C2....]

    Returns an expanded *groupid* and the *value1...valueN*, perfoming new groupings when subsequent rows *date* values differ more than *maxdiff* milliseconds. Rows grouped together
    are the ones that order by *orderby* column or if ommited by the given order have less *date* distance than *maxdiff*. Input dates should be in :ref:`ISO 8601 format <iso8601>`.

    :Returned multiset schema:
        - *bgroupid*
            *groupid* appended with an integer value indicating the subgroup of the row.
        - *C1, C2 ..*
            The input values of the row.

    .. seealso::

       * :ref:`tutmultiset` functions

    >>> table1('''
    ... 1 session1 '2007-01-01 00:03:13'
    ... 2 session1 '2007-01-01 00:03:27'
    ... 3 session1 '2007-01-01 00:03:36'
    ... 4 session2 '2007-01-01 00:04:39'
    ... 5 session2 '2007-01-01 00:04:40'
    ... 6 session3 '2007-01-01 00:04:49'
    ... 7 session3 '2007-01-01 00:04:59'
    ... ''')
    >>> sql("select datediffbreak(b,a,c,10*1000,'order',c,a) from table1 group by b")
    bgroupid  | C1
    --------------
    session10 | 1
    session11 | 2
    session11 | 3
    session20 | 4
    session20 | 5
    session30 | 6
    session30 | 7

.. doctest::
    :hide:

    >>> sql("select datediffbreak(b,c,c='open',a) from (select 4 as a, 6 as b, 9 as c where c!=9)")
    bgroupid | C1
    ---------------
    None     | None
    >>> sql("select datediffbreak(b,a,c,10*1000,a,c) from table1 group by b")
    Traceback (most recent call last):
    ...
    OperatorError: Madis SQLError: 
    Operator DATEDIFFBREAK: Wrong date format: 1
    """
    registered=True
    multiset=True


    def __init__(self):
        self.vals=[]
        self.first=True
        self.position=None
        self.comparesize=0
        self.fullsize=0

    def step(self, *args):

        if not args:
            raise functions.OperatorError("datediffbreak","No arguments")
        if len(args)<4:
            raise functions.OperatorError("datediffbreak","Wrong number of arguments")
        if self.first:
            self.first=False
            self.maxdiff=args[-1]
            for i in xrange(len(args)):
                if args[i]=='order':
                    self.position=i
                    self.maxdiff=args[i-1]
                    self.comparesize=len(args)-(i+1)

                    if len(args)<5:
                        raise functions.OperatorError("datediffbreak","Wrong number of arguments")
                    break

        if not self.position:
            self.vals.append(list(args[:-1]))
        else:
            self.vals.append(list(args[:self.position-1]+args[self.position+1:]))


    def final(self):
        if self.position:
            self.vals.sort(key=lambda x:tuple(x[-self.comparesize:]))
        if self.vals==[]:
            size=0
        else:
            size=len(self.vals[0])-self.comparesize-1

        from lib.buffer import CompBuffer
        a=CompBuffer()
        if size<=0:
            a.writeheader(["bgroupid","C1"])
            a.write(["None","None"])
            return a.serialize()
        a.writeheader(["bgroupid"]+["C"+str(i+1) for i in xrange(size-1)])

        counter=0
        dt=None
        dtpos=self.comparesize+1
        for el in self.vals:
            try:
                dtnew=iso8601.parse_date(el[-dtpos])
            except Exception:
                raise functions.OperatorError("datediffbreak","Wrong date format: %s" %(el[-dtpos]))
            if dt and timedelta2millisec(dtnew-dt)>self.maxdiff:
                counter+=1
            dt=dtnew
            bid=unistr(el[0])+str(counter)
            a.write([bid]+el[1:-dtpos])

        return a.serialize()



class datedifffilter:
    """

    .. function:: datedifffilter(maxdiff, date, C1, C2 ....) -> [date,C1,C2....]

    Returns only a subset of the provided entries, performing a sort of entry clustering based on the entries date difference. Each cluster is 
    represented by the latest entry. 
    The first argument defines the time differnece threshold that is employed for entry clustering, and it is provided in seconds.
    The second argument is assumed to contain the date column. Entries are assumed to be provided in an ascending order by the date column. 
    Input dates should be in :ref:`ISO 8601 format <iso8601>`.
    All subsequent columns remain unchanged.


    :Returned multiset schema:
        - *date, C1, C2 ..*
            The selected input values of the row.

    .. seealso::

       * :ref:`tutmultiset` functions

    >>> table1('''
    ... 2010-01-01T01:32:03Z value1
    ... 2010-01-01T01:32:04Z value2
    ... 2010-01-01T01:32:06Z value3
    ... 2010-01-01T01:32:08Z value4
    ... 2010-01-01T01:32:29Z value5
    ... 2010-01-01T02:35:03Z value6
    ... 2010-01-01T02:35:04Z value7
    ... 2010-01-01T03:55:04Z value8
    ... ''')
    >>> sql("select datedifffilter(20, a,b) from table1")
    date                 | C1
    -----------------------------
    2010-01-01T01:32:08Z | value4
    2010-01-01T01:32:29Z | value5
    2010-01-01T02:35:04Z | value7
    2010-01-01T03:55:04Z | value8

    >>> table1('''
    ... 2010-01-01T01:32:03Z value1
    ... ''')
    >>> sql("select datedifffilter(20, a,b) from table1")
    date                 | C1
    -----------------------------
    2010-01-01T01:32:03Z | value1

    >>> table1('''
    ... '2010-01-01 01:32:03' value1
    ... '2010-01-01 01:32:04' value2
    ... '2010-01-01 01:32:06' value3
    ... '2010-01-01 01:32:08' value4
    ... '2010-01-01 01:32:29' value5
    ... '2010-01-01 02:35:03' value6
    ... '2010-01-01 02:35:04' value7
    ... '2010-01-01 03:55:04' value8
    ... ''')
    >>> sql("select datedifffilter(30, a,b) from table1")
    date                | C1
    ----------------------------
    2010-01-01 01:32:29 | value5
    2010-01-01 02:35:04 | value7
    2010-01-01 03:55:04 | value8

    """
    registered=True
    multiset=True


    def __init__(self):
        self.init=True
        self.vals=[]
        self.maxdiff=0
        self.counter=0
        self.tablesize=0


    def initargs(self, args):
        self.init=False
        if not args:
            raise functions.OperatorError("datedifffilter","No arguments")
        if len(args)<2:
            raise functions.OperatorError("datedifffilter","Wrong number of arguments")
        self.tablesize=len(args)-1
        self.maxdiff=args[0]

    def step(self, *args):
        if self.init==True:
            self.initargs(args)

        self.vals.append(list(args[1:]))
        self.counter+=1

    def final(self):
        
        if self.tablesize<=0:
            yield ("date","C1")
            yield [None,None]
            return

        yield tuple(["date"]+["C"+str(i) for i in xrange(1,self.tablesize)])
        
        dt=None
        dtpos=0
        diff=0
        if self.counter==1:
            yield(self.vals[dtpos])
        else:
            tmpvalsdt=[x[0] for x in self.vals]
            for el in self.vals:
                el.insert(0,iso8601.parse_date(el[0]))
            self.vals.sort(key=itemgetter(0))
            for el in self.vals:
                if dtpos<self.counter-1:
                    dt = el[0]
                    dtnew =self.vals[dtpos+1][0]
                    diff=dtnew-dt
                    dtpos+=1
                    if (diff.days*86400+diff.seconds)>self.maxdiff:
                        yield(el[1:])
                    if dtpos==self.counter-1:
                        yield(self.vals[dtpos][1:])

class datediffgroup:
    """

    .. function:: datediffgroup(maxdiff, date, C1, C2 ....) -> [groupid, date,C1,C2....]

    Performing a sort of entry clustering based on the entries date difference.
    The cluster id that is assigned to each entry is reutrned in the first column, and it is followed by the entry's original contents.

    The first argument defines the time differnece threshold that is employed for entry clustering, and it is provided in seconds.
    The second argument is assumed to contain the date column. Entries are assumed to be provided in an ascending order by the date column.
    Input dates should be in :ref:`ISO 8601 format <iso8601>`.
    All subsequent columns remain unchanged.


    :Returned multiset schema:
        - *date, C1, C2 ..*
            The selected input values of the row.

    .. seealso::

       * :ref:`tutmultiset` functions

    >>> table1('''
    ... 2010-01-01T01:32:03Z value1
    ... 2010-01-01T01:32:04Z value2
    ... 2010-01-01T01:32:06Z value3
    ... 2010-01-01T01:32:08Z value4
    ... 2010-01-01T01:32:29Z value5
    ... 2010-01-01T02:35:03Z value6
    ... 2010-01-01T02:35:04Z value7
    ... 2010-01-01T03:55:04Z value8
    ... ''')
    >>> sql("select datediffgroup(20,a,b) from table1")
    groupid | date                 | C1
    ---------------------------------------
    1       | 2010-01-01T01:32:03Z | value1
    1       | 2010-01-01T01:32:04Z | value2
    1       | 2010-01-01T01:32:06Z | value3
    1       | 2010-01-01T01:32:08Z | value4
    2       | 2010-01-01T01:32:29Z | value5
    3       | 2010-01-01T02:35:03Z | value6
    3       | 2010-01-01T02:35:04Z | value7
    4       | 2010-01-01T03:55:04Z | value8
    """
    registered=True
    multiset=True


    def __init__(self):
        self.init=True
        self.vals=[]
        self.maxdiff=0
        self.counter=0
        self.tablesize=0
        self.groupIdCounter=1


    def initargs(self, args):
        self.init=False
        if not args:
            raise functions.OperatorError("datediffgroup","No arguments")
        if len(args)<2:
            raise functions.OperatorError("datediffgroup","Wrong number of arguments")
        self.tablesize=len(args)-1
        self.maxdiff=args[0]



    def step(self, *args):
        if self.init==True:
            self.initargs(args)

        self.vals.append(list(args[1:]))
        self.counter+=1

    def final(self):

        from lib.buffer import CompBuffer
        a=CompBuffer()
        if self.tablesize<=0:
            a.writeheader(["groupid","date","C1"])
            a.write(["None","None","None"])
            return a.serialize()
        a.writeheader(["groupid"]+["date"]+["C"+str(i+1) for i in xrange(self.tablesize-1)])


        dt=None
        dtpos=0
        diff=0

        for el in self.vals:
            
            if dtpos<self.counter-1:
                dt = iso8601.parse_date(el[0])
                dtnew =iso8601.parse_date(self.vals[dtpos+1][0])
                diff=dtnew-dt
                a.write([str(self.groupIdCounter)]+el)
                if (diff.days*24*60*60+diff.seconds)>self.maxdiff:
                    self.groupIdCounter+=1
                
                dtpos+=1
                if dtpos==self.counter-1:
                    a.write([str(self.groupIdCounter)]+self.vals[dtpos])

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

