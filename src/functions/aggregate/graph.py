__docformat__ = 'reStructuredText en'

import json
from hashlib import md5
from binascii import b2a_base64
import math

class graphpowerhash:
    """
    .. function:: graphpowerhash(steps, [undirected_edge], node1, node2, [node1_details, edge_details, node2_details]) -> jpack of graph node hashes

    Graph power hashing is based on a `power iteration algorithm <http://en.wikipedia.org/wiki/Power_iteration>`_
    that calculates hashes on every processing step. The produced output, contains for every node in the input graph
    a hash that "describes" its "surroundings".

    :'steps' parameter:
        The *steps* option controls the number of steps that the power hashing will be executed. Another
        way to conceptualize the *steps* parameter is to think of it as the radius of the graph around
        a particular node that the node's hash covers.

        Steps parameter's possible value are:

        - null (default). When steps=null, then steps is automatically set to number_of_nodes/2
        - Positive integer value.
        - -1 . Steps is set to number_of_nodes
        - Negative integers, steps is set to number_of_nodes / absolute_value(steps)

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

    .. note::
        The computational complexity of the powerhash algorithm is O(n * steps * average_node_degree). The optimal value for
        the hash to fully cover the graph, is to set the steps parameter to *graph_diameter* / 2.
        
        Right now for steps=null, we take the worse upper bound of n / 2, so the computational complexity becomes
        O(n * ~(n/2) * average_node_degree).

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
    ["OaNj+OtIZPqcwjc3QVvKpg","Um7OU79ApcRNA2TKrdcBcA","ZyQT/AoKyjIkwWMNvceK2A","3vaHWSLU/H32HvHTVBkpUQ","+3uZjYUMSXwyZs7HFHKNVg"]


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
    ["OaNj+OtIZPqcwjc3QVvKpg","Um7OU79ApcRNA2TKrdcBcA","ZyQT/AoKyjIkwWMNvceK2A","3vaHWSLU/H32HvHTVBkpUQ","+3uZjYUMSXwyZs7HFHKNVg"]


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
    ["APq1eISun1GpYjgUhiMrLA","NPPh9FLzC5cUedxldXV77Q","VVZ93zo6gePuMeRf6f00Zg","df/4yDABlitCTfOGut0NvA","lqo+lY4fcjqujlgsYr+3Yw"]


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
    -----------------------------
    ["TOiuilAk4RLkg01tIwyvcg"]


    Undirected version of table1's graph:

    >>> sql("select graphpowerhash(null, null, a,b) from table1")
    graphpowerhash(null, null, a,b)
    ------------------------------------------------------------------------------------------------------------------------------
    ["JudlYSkYV7rFHjk94abY/A","W88IN4kgDSeVX9kaY36SJg","W88IN4kgDSeVX9kaY36SJg","6ez9ee0N2ogdvKJVQ8VKWA","7gz+LT/LtsyFc+GxMUlL8g"]


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
    ["JudlYSkYV7rFHjk94abY/A","W88IN4kgDSeVX9kaY36SJg","W88IN4kgDSeVX9kaY36SJg","6ez9ee0N2ogdvKJVQ8VKWA","7gz+LT/LtsyFc+GxMUlL8g"]


    Graph similarity, using the step parameter (value of step defines the radius of the similar subgraphs that can be found):

    >>> sql("select jaccard( (select graphpowerhash(3, a, b) from table1), (select graphpowerhash(3, a, b) from table3) ) as jacsim")
    jacsim
    ------
    0.0

    >>> sql("select jaccard( (select graphpowerhash(1, a, b) from table1), (select graphpowerhash(1, a, b) from table3) ) as jacsim")
    jacsim
    ------
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
    ["Rw3sDN24TI7YARBNOOmYSg","9m5wcZf9iUxDwgzQkzu6Ag","9m5wcZf9iUxDwgzQkzu6Ag"]


    Second with all details:

    >>> sql("select graphpowerhash(null, null, a, b, c, d, e) from table5")
    graphpowerhash(null, null, a, b, c, d, e)
    ----------------------------------------------------------------------------
    ["CPebw+eZYzw5bWgx47/tkg","CPebw+eZYzw5bWgx47/tkg","WNn4aDDBKcoMMi+nrz5JEA"]

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
        ncount=len(self.nodes)

        for n,v in self.nodes.iteritems():
            v[1]=str(len(v[0]))+chr(31)+v[1]

        if ncount==1:
            self.steps=1

        if self.steps==None:
            # Calculate approximate worse case diameter
            degreeseq=set()
            mindegree=ncount
            maxdegree=0
            invdegree=0.0

            for n,v in self.nodes.iteritems():
                ndegree=len(v[0])
                mindegree=min(mindegree, ndegree)
                maxdegree=max(maxdegree, ndegree)
                degreeseq.add(ndegree)
                invdegree+=1.0/ndegree

            self.steps=int(min(
            # Obvious upper bound
            ncount-max(2, maxdegree) + 2,
            # P. Dankelmann "Diameter and inverse degree"
            (3*invdegree+3)*math.log(ncount)/math.log(math.log(ncount)),
            # Simon Mukwembi "A note on diameter and the degree sequence of a graph"
            1+3*(ncount - len(degreeseq)+1)/float((mindegree+1)), ncount - len(degreeseq)+2))/2

        if self.steps<0:
            self.steps=ncount/abs(self.steps)

        nhashes={}

        for n,v in self.nodes.iteritems():
            nhashes[n]=md5(str(v[1]+chr(30))).digest()

        if ncount>1:
            for s in xrange(self.steps):
                nhashes1={}
                nhashcount={}
                for n, v in self.nodes.iteritems():
                    nhash=md5(v[1]+chr(30)+chr(30).join(sorted([nhashes[x]+chr(29)+y for x,y in v[0]]))).digest()
                    nhashes1[n]=nhash
                    if nhash in nhashcount:
                        nhashcount[nhash]+=1
                    else:
                        nhashcount[nhash]=1
                nhashes=nhashes1

#                TODO Find new upper bound of diameter via calculating Spanning Tree starting from distincthash
#                if len(nhashcount)>0:
#                    distincthash=min([x for x,y in nhashcount.iteritems() if y==1])


        return json.dumps([b2a_base64(x)[0:-3] for x in sorted(nhashes.values())], separators=(',',':'), ensure_ascii=False)

class graphtodot:
    """
    .. function:: graphtodot(graphname, [undirected_edge], node1, node2, [node1_details, edge_details, node2_details]) -> graphviz dot graph

    Returns the *Graphviz* DOT representation of the input graph.

    Examples:

    Directed graph:

    >>> table1('''
    ... 1   2
    ... 2   3
    ... 3   4
    ... 4   5
    ... 5   3
    ... ''')

    >>> sql("select graphtodot(null, a,b) from table1")
    graphtodot(null, a,b)
    ----------------------------------------------------
    digraph  {
    1 -> 2;
    2 -> 3;
    3 -> 4;
    4 -> 5;
    5 -> 3;
    }

    Undirected graph:

    >>> table2('''
    ... 2   5
    ... 5   4
    ... 4   1
    ... 1   3
    ... 3   4
    ... ''')

    >>> sql("select graphtodot(null, null, a,b) from table2")
    graphtodot(null, null, a,b)
    --------------------------------------------------
    graph  {
    1 -- 3;
    2 -- 5;
    3 -- 4;
    4 -- 1;
    5 -- 4;
    }

    Graph with details:

    >>> table5('''
    ... 1   2   O   =   C
    ... 2   3   C   =   O
    ... ''')

    >>> sql("select graphtodot('chem_comp_1', null, a, b, c, d, e) from table5")
    graphtodot('chem_comp_1', null, a, b, c, d, e)
    ----------------------------------------------------------------------------------------------------------
    graph chem_comp_1 {
    1 [label="O"];
    1 -- 2 [label="="];
    2 [label="C"];
    2 -- 3 [label="="];
    3 [label="O"];
    }

    """

    registered=True

    def __init__(self):
        self.nodes={}
        self.steps=None
        self.graphname=None
        self.directed=True

    def step(self, *args):
        directed=True
        argslen=len(args)
        largs=args

        if largs[0]!=None:
            self.graphname=largs[0]

        if largs[1]==None:
            self.directed=False
            largs=list(largs)
            del(largs[1])
            argslen-=1

        if self.directed:
            if argslen>4:
                edgedetailslr=unicode(largs[4])
            else:
                edgedetailslr=None
        else:
            if argslen>4:
                edgedetailslr=unicode(largs[4])
            else:
                edgedetailslr=None

        if largs[1] not in self.nodes:
            if argslen>3:
                self.nodes[largs[1]]=[ [( largs[2],edgedetailslr )] , largs[3]]
            else:
                self.nodes[largs[1]]=[ [( largs[2],edgedetailslr )] , None]
        else:
            self.nodes[largs[1]][0].append( ( largs[2],edgedetailslr ) )


        if largs[2]!=None:
            if largs[2] not in self.nodes:
                if argslen>5:
                    self.nodes[largs[2]]=[ [], largs[5]]
                else:
                    self.nodes[largs[2]]=[ [] , None]

    def final(self):
        if self.graphname==None:
            self.graphname=''

        if type(self.graphname) in (int, float):
            self.graphname=u'g'+unicode(self.graphname)
        else:
            self.graphname=unicode(self.graphname)
        
        dot=u''
        if self.directed:
            dot=u'di'

        if self.graphname==None:
            self.graphname='""'

        dot+=u'graph '+self.graphname+u' {\n'

        digraph=False
        
        for n,v in self.nodes.iteritems():
            if v[1]!=None:
                dot+=unicode(n)+' [label="'+unicode(v[1]).replace('"',"'")+'"];\n'
            for e in v[0]:
                dot+=unicode(n)+ ' '
                if self.directed:
                    dot+='-> '
                else:
                    dot+='-- '
                dot+=unicode(e[0])
                if e[1]!=None:
                    dot+=u' [label="'+unicode(e[1]).replace('"',"'")+'"]'
                dot+=u';\n'

        dot+='}'

        return dot

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
