__docformat__ = 'reStructuredText en'

import math
import json
from hashlib import md5

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
    --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    ["461b9cab7c9eb7f2447197046b9f8411","5e826a28aeeed67c88abe22e2281be77","6ad8822a3138898ece6d4915b0a1a4d3","92a94668fb647318476eec6b35e72ded","eeeb2d3b94154ee185c7e899e153c432"]

    >>> table2('''
    ... 2   5
    ... 5   4
    ... 4   1
    ... 1   3
    ... 3   4
    ... ''')
    >>> sql("select graphpowerhash(null, a,b) from table2")
    graphpowerhash(null, a,b)
    --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    ["461b9cab7c9eb7f2447197046b9f8411","5e826a28aeeed67c88abe22e2281be77","6ad8822a3138898ece6d4915b0a1a4d3","92a94668fb647318476eec6b35e72ded","eeeb2d3b94154ee185c7e899e153c432"]
    
    >>> table3('''
    ... 2   5
    ... 5   4
    ... 4   1
    ... 1   3
    ... 3   2
    ... ''')
    >>> sql("select graphpowerhash(null, a,b) from table3")
    graphpowerhash(null, a,b)
    --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    ["213a1fd70e934d1924cdc885037393cc","213a1fd70e934d1924cdc885037393cc","213a1fd70e934d1924cdc885037393cc","213a1fd70e934d1924cdc885037393cc","213a1fd70e934d1924cdc885037393cc"]

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
                edgedetailslr='1'+chr(30)+unicode(args[4])
                edgedetailsrl='0'+chr(30)+unicode(args[4])
            else:
                edgedetailslr='1'
                edgedetailsrl='0'
        else:
            if argslen>4:
                edgedetailslr='1'+ chr(30)+unicode(args[4])
                edgedetailsrl=edgedetailslr
            else:
                edgedetailslr='1'
                edgedetailsrl=edgedetailslr

        if args[1] not in self.nodes:
            if argslen>3:
                self.nodes[args[1]]=[ [( args[2],edgedetailslr )] , args[3]]
            else:
                self.nodes[args[1]]=[ [( args[2],edgedetailslr )] , u'']
        else:
            self.nodes[args[1]][0].append( ( args[2],edgedetailslr ) )


        if args[2] not in self.nodes:
            if argslen>5:
                self.nodes[args[2]]=[ [(args[1],edgedetailsrl )], args[5]]
            else:
                self.nodes[args[2]]=[ [(args[1],edgedetailsrl )] , u'']
        else:
            self.nodes[args[2]][0].append( ( args[1],edgedetailsrl ) )

    def final(self):
        if self.steps==None:
            self.steps=int(math.sqrt(len(self.nodes)))
            
        nhashes={}

        for n,v in self.nodes.iteritems():
            nhashes[n]=md5(v[1]).hexdigest()

        for s in xrange(self.steps):
            nhashes1={}
            for n, v in self.nodes.iteritems():
                nhashes1[n]=md5(v[1]+chr(30)+chr(30).join(sorted([nhashes[x]+chr(30)+y for x,y in v[0]]))).hexdigest()
            nhashes=nhashes1

        return json.dumps(sorted(nhashes.values()), separators=(',',':'), ensure_ascii=False)

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
