__docformat__ = 'reStructuredText en'

import math
import json
from hashlib import md5
from binascii import b2a_hqx

def hashlist(t):
    return md5(chr(30).join(unicode(x) for x in t)).digest()

class graphpowerhash:
    """
    .. function:: graphpowerhash(steps, node1, [undirected_edge], node2, [node1_details, edge_details, node2_details]) -> jpack of graph node hashes

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

    """

    registered=True

    def __init__(self):
        self.nodes={}
        self.steps=None
        self.initialized=False

    def step(self, *args):
        directed=True
        argslen=len(args)

        if args[0]!=None:
            self.steps=args[0]

        if args[2]==None:
            directed=False
            del(args[2])
            argslen-=1

        if directed:
            if argslen>4:
                edgedetailslr='1'+chr(30)+str(args[4])
                edgedetailsrl='0'+chr(30)+str(args[4])
            else:
                edgedetailslr='1'
                edgedetailsrl='0'
        else:
            if argslen>4:
                edgedetailslr='1'+ chr(30)+str(args[4])
                edgedetailsrl=edgedetailslr
            else:
                edgedetailslr='1'
                edgedetailsrl=edgedetailslr

        if args[1] not in self.nodes:
            if argslen>3:
                self.nodes[args[1]]=[ [( args[2],edgedetailslr )] , str(args[3])]
            else:
                self.nodes[args[1]]=[ [( args[2],edgedetailslr )] , '']
        else:
            self.nodes[args[1]][0].append( ( args[2],edgedetailslr ) )


        if args[2] not in self.nodes:
            if argslen>5:
                self.nodes[args[2]]=[ [(args[1],edgedetailsrl )], str(args[5])]
            else:
                self.nodes[args[2]]=[ [(args[1],edgedetailsrl )] , '']
        else:
            self.nodes[args[2]][0].append( ( args[1],edgedetailsrl ) )

    def final(self):
        if self.steps==None:
            self.steps=1+len(self.nodes)/2

        if self.steps==-1:
            self.steps=len(self.nodes)

        self.steps=min(self.steps, len(self.nodes))

        nhashes={}

        for n,v in self.nodes.iteritems():
            nhashes[n]=str(v[1])

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
