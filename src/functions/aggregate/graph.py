__docformat__ = 'reStructuredText en'

import math
import json
from hashlib import md5
from binascii import b2a_hqx

def hashlist(t):
    return md5(chr(30).join(unicode(x) for x in t)).digest()

class graphpowerhash:
    """
    .. function:: graphpowerhash(steps, [undirected_edge], node1, node2, [node1_details, edge_details, node2_details]) -> jpack of graph node hashes

    Example:

    >>> table1('''
    ... 1   2
    ... 2   3
    ... 3   4
    ... 4   5
    ... 5   3
    ... ''')
    >>> sql("select graphpowerhash(null, a,b) from table1")
    graphpowerhash(null, a,b)
    ------------------------------------------------------------------------------------------------------------------------------
    [",m6pFc4eEFE+SDG++9fb``","1C&%ibj3lPB)E[GiaM3eK!","VMIk)Jmf)S&a2CN5EB3VTJ","e!Fr9@M![!!238r0rV#1iJ","if-#Cqpj,ebY3H'l'r9Fb3"]

    >>> table2('''
    ... 2   5
    ... 5   4
    ... 4   1
    ... 1   3
    ... 3   4
    ... ''')
    >>> sql("select graphpowerhash(null, a,b) from table2")
    graphpowerhash(null, a,b)
    ------------------------------------------------------------------------------------------------------------------------------
    [",m6pFc4eEFE+SDG++9fb``","1C&%ibj3lPB)E[GiaM3eK!","VMIk)Jmf)S&a2CN5EB3VTJ","e!Fr9@M![!!238r0rV#1iJ","if-#Cqpj,ebY3H'l'r9Fb3"]
    
    >>> table3('''
    ... 2   5
    ... 5   4
    ... 4   1
    ... 1   3
    ... 3   2
    ... ''')
    >>> sql("select graphpowerhash(null, a,b) from table3")
    graphpowerhash(null, a,b)
    ------------------------------------------------------------------------------------------------------------------------------
    ["fUGhcEl*M19afABBMG#BSJ","fUGhcEl*M19afABBMG#BSJ","fUGhcEl*M19afABBMG#BSJ","fUGhcEl*M19afABBMG#BSJ","fUGhcEl*M19afABBMG#BSJ"]

    >>> sql("select hashmd5( (select graphpowerhash(null, a,b) from table1) )=hashmd5( (select graphpowerhash(null, a,b) from table2) ) as grapheq")
    grapheq
    -------
    1

    >>> sql("select hashmd5( (select graphpowerhash(null, a,b) from table1) )=hashmd5( (select graphpowerhash(null, a,b) from table3) ) as grapheq")
    grapheq
    -------
    0

    >>> sql("select graphpowerhash(null, a, null) from (select * from table1 limit 1)")
    graphpowerhash(null, a, null)
    ----------------------------------
    ["C5*Q,@C#E5&B5MC85L&43Q`b5b0*5J"]

    """

    registered=True

    def __init__(self):
        self.nodes={}
        self.steps=None
        self.initialized=False

    def step(self, *args):
        directed=True
        argslen=len(args)
        largs=args

        if largs[0]!=None:
            self.steps=largs[0]

        if largs[1]==None:
            directed=False
            largs=list(largs)
            del(largs[1])
            argslen-=1

        if directed:
            if argslen>4:
                edgedetailslr='1'+chr(30)+str(largs[4])
                edgedetailsrl='0'+chr(30)+str(largs[4])
            else:
                edgedetailslr='1'
                edgedetailsrl='0'
        else:
            if argslen>4:
                edgedetailslr='1'+ chr(30)+str(largs[4])
                edgedetailsrl=edgedetailslr
            else:
                edgedetailslr='1'
                edgedetailsrl=edgedetailslr

        if largs[1] not in self.nodes:
            if argslen>3:
                self.nodes[largs[1]]=[ [( largs[2],edgedetailslr )] , str(largs[3])]
            else:
                self.nodes[largs[1]]=[ [( largs[2],edgedetailslr )] , '']
        else:
            self.nodes[largs[1]][0].append( ( largs[2],edgedetailslr ) )


        if largs[2]!=None:
            if largs[2] not in self.nodes:
                if argslen>5:
                    self.nodes[largs[2]]=[ [(largs[1],edgedetailsrl )], str(largs[5])]
                else:
                    self.nodes[largs[2]]=[ [(largs[1],edgedetailsrl )] , '']
            else:
                self.nodes[largs[2]][0].append( ( largs[1],edgedetailsrl ) )

    def final(self):
        if self.steps==None:
            self.steps=len(self.nodes)/2

        if self.steps==-1:
            self.steps=len(self.nodes)

        self.steps=min(self.steps, len(self.nodes))

        nhashes={}

        for n,v in self.nodes.iteritems():
            nhashes[n]=b2a_hqx(md5(str(v[1])).digest())

        for s in xrange(self.steps):
            nhashes1={}
            for n, v in self.nodes.iteritems():
                nhashes1[n]=md5(v[1]+chr(30)+chr(30).join(sorted([nhashes[x]+chr(30)+y for x,y in v[0]]))).digest()
            nhashes=nhashes1

        return json.dumps([b2a_hqx(x) for x in sorted(nhashes.values())], separators=(',',':'), ensure_ascii=False)

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
