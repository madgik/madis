__docformat__ = 'reStructuredText en'

import json
from hashlib import md5
from binascii import b2a_base64

class graphpowerhash:
    """
    .. function:: graphpowerhash(steps, [undirected_edge], node1, node2, [node1_details, edge_details, node2_details]) -> jpack of graph node hashes

    Graph power hashing is based on a `power iteration algorithm <http://en.wikipedia.org/wiki/Power_iteration>`_
    that calculates hashes on every processing step. The produced output, contains for every node in the input graph
    a hash that "describes" its "surroundings".

    :'steps' parameter:
        The *steps* option controls the number of steps that the power hashing will be executed. Another
        way to conceptualize the *steps* parameter is to think of it as the radius of the graph arround
        a particular node that the node's hash covers.

        Steps parameter's possible value are:

        - null (default). When steps=null, then steps is automatically set to number_of_nodes/2
        - 0 . Steps is automatically set to number_of_nodes
        - Positive integer value.

    :'undirected_edge':

        This option can only have the *null* value.

        - Parameter absent. The graph is assumed to be directed.
        - Parameter present and having a *null* value. The graph is assumed to be undirected

    :node1, node2:

        Node connections. If the graph contains only one node, then *node2* can be null.

    :node and edge details:

        Optional details, that are processed with the graph's structure. In essence these
        parameters define "tags" on the nodes and edges of the graph.

    .. note::
        The graph power hash algorithm is an experimental algorithm (created by me, Lefteris Stamatogiannakis). I haven't
        proved its correctness, so please use it with care. Due to its hash usage, there is a (very low probability)
        that two different graphs could hash to the same power hash.

        I would be very very thankfull to anyone knowledgable in graph theory, who could prove it to be wrong (or correct).
        Also while i've searched in the related bibliography, i couldn't find anything close to power hash algorithm. Nevertheless
        if anyone knows of a paper that describes anything related to this algorithm, i would be glad to be pointed towards it.

    
    Examples:

    Directed graph:

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
    ["H9QIfSVjX6RT/x/32Kcxkg","PoWLphNw6TxUil3VmMtXeA","VfSxS5Y3XiKV+CabsH2XHQ","rrLGbHg8DkES8bhNKbN9QA","wHwTkZ2uLDtxnUMqtaIoBQ"]


    Above graph having its nodes renumbered (its powerhash is the same as above):

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
    ["H9QIfSVjX6RT/x/32Kcxkg","PoWLphNw6TxUil3VmMtXeA","VfSxS5Y3XiKV+CabsH2XHQ","rrLGbHg8DkES8bhNKbN9QA","wHwTkZ2uLDtxnUMqtaIoBQ"]


    Above graph with a small change (its hash differs from above graphs):

    >>> table3('''
    ... 2   5
    ... 5   4
    ... 4   1
    ... 1   3
    ... 3   5
    ... ''')

    >>> sql("select graphpowerhash(null, a,b) from table3")
    graphpowerhash(null, a,b)
    ------------------------------------------------------------------------------------------------------------------------------
    ["A4LPCs61OwqZwNO8Nhpgtg","C+JyRaUUSq50VBmFF6bTDg","rrLGbHg8DkES8bhNKbN9QA","wHwTkZ2uLDtxnUMqtaIoBQ","x/aHwL5b/J1kp7VnIUXjFg"]


    Actual testing of equality or inequality of above graphs:

    >>> sql("select hashmd5( (select graphpowerhash(null, a,b) from table1) )=hashmd5( (select graphpowerhash(null, a,b) from table2) ) as grapheq")
    grapheq
    -------
    1

    >>> sql("select hashmd5( (select graphpowerhash(null, a,b) from table1) )=hashmd5( (select graphpowerhash(null, a,b) from table3) ) as grapheq")
    grapheq
    -------
    0


    Graph with only one node:

    >>> sql("select graphpowerhash(null, a, null) from (select * from table1 limit 1)")
    graphpowerhash(null, a, null)
    --------------------------------------
    ["ZThjcUIyZlNONzVOb3dyT0dSck53Zz09Cg"]


    Undirected version of table1's graph:

    >>> sql("select graphpowerhash(null, null, a,b) from table1")
    graphpowerhash(null, null, a,b)
    ------------------------------------------------------------------------------------------------------------------------------
    ["COSM7uS7fo3Ed/7HWWR+YQ","FtwRgMdJfnNT7ASFUUOjrg","M/H66vwrvarGfY1w8K5MNQ","M/H66vwrvarGfY1w8K5MNQ","phZ+V0esCA2Ko88WWdUjxw"]


    Same graph as above, but some of the edges have been reversed (the undirected powerhash matches the powerhash above):

    >>> table4('''
    ... 2   1
    ... 2   3
    ... 3   4
    ... 4   5
    ... 3   5
    ... ''')

    >>> sql("select graphpowerhash(null, null, a,b) from table4")
    graphpowerhash(null, null, a,b)
    ------------------------------------------------------------------------------------------------------------------------------
    ["COSM7uS7fo3Ed/7HWWR+YQ","FtwRgMdJfnNT7ASFUUOjrg","M/H66vwrvarGfY1w8K5MNQ","M/H66vwrvarGfY1w8K5MNQ","phZ+V0esCA2Ko88WWdUjxw"]


    Graph similarity, using the step parameter (value of step defines the diameter of the similar subgraphs that can be found):

    >>> sql("select jaccard( (select graphpowerhash(4, a, b) from table1), (select graphpowerhash(4, a, b) from table3) )")
    jaccard( (select graphpowerhash(4, a, b) from table1), (select graphpowerhash(4, a, b) from table3) )
    -----------------------------------------------------------------------------------------------------
    0.0

    >>> sql("select jaccard( (select graphpowerhash(2, a, b) from table1), (select graphpowerhash(2, a, b) from table3) )")
    jaccard( (select graphpowerhash(2, a, b) from table1), (select graphpowerhash(2, a, b) from table3) )
    -----------------------------------------------------------------------------------------------------
    0.25


    Powerhash of graph having details (using a chemical composition):
    
    >>> table5('''
    ... 1   2   O   =   C
    ... 2   3   C   =   O
    ... ''')

    First without details:

    >>> sql("select graphpowerhash(null, null, a, b) from table5")
    graphpowerhash(null, null, a, b)
    ----------------------------------------------------------------------------
    ["bGKfTizvbWHa0dwm/I0o3A","bGKfTizvbWHa0dwm/I0o3A","ib+7InK2s/mVeUDM6owETg"]


    Second with all details:

    >>> sql("select graphpowerhash(null, null, a, b, c, d, e) from table5")
    graphpowerhash(null, null, a, b, c, d, e)
    ----------------------------------------------------------------------------
    ["u6DcfG+uNbT1wLy/nInKeA","3QUN3ktUN/oWzgV1CfLMKw","3QUN3ktUN/oWzgV1CfLMKw"]

    >>>

    """

    registered=True

    def __init__(self):
        self.nodes={}
        self.steps=None

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

        if self.steps<=0:
            self.steps=len(self.nodes)

        self.steps=min(self.steps, len(self.nodes))

        nhashes={}

        for n,v in self.nodes.iteritems():
            nhashes[n]=b2a_base64(md5(str(v[1]+chr(30))).digest())

        if len(self.nodes)>1:
            for s in xrange(self.steps):
                nhashes1={}
                for n, v in self.nodes.iteritems():
                    nhashes1[n]=md5(v[1]+chr(30)+chr(30).join(sorted([nhashes[x]+chr(29)+y for x,y in v[0]]))).digest()
                nhashes=nhashes1

        return json.dumps([b2a_base64(x)[0:-3] for x in sorted(nhashes.values())], separators=(',',':'), ensure_ascii=False)

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