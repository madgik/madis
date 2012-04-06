"""

.. function:: pipe(query:None[,lines:t])

Executes *query* as a shell command and returns the standard output lines as rows of one column table. Setting *lines* parameter to *f* the command output will be returned in one table row.


:Returned table schema:
    - *output* text
        Output of shell command execution


Examples::

.. doctest::

    >>> sql("pipe wc ./testing/colpref.csv")
    C1
    ---------------------------------
     19  20 463 ./testing/colpref.csv
    <BLANKLINE>

.. doctest::
    :hide:
    
    >>> sql("pipe wc nonexistingfile") #doctest:+ELLIPSIS +NORMALIZE_WHITESPACE
    Traceback (most recent call last):
    ...
    OperatorError: Madis SQLError:
    Operator PIPE: Command 'wc nonexistingfile' failed to execute because:
    wc: nonexistingfile: No such file or directory
"""


import setpath
import functions
from vtiterable import SourceVT


import subprocess

registered=True

class PipeCursor:
    def __init__(self,command,lines):
        child=subprocess.Popen(command,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        output, error = child.communicate()
        if child.returncode!=0:
            raise functions.OperatorError(__name__.rsplit('.')[-1],"Command '%s' failed to execute because:\n%s" %(command,error.rstrip('\n\t ')))
        output=unicode(output,'utf-8')
        if not lines:
            self.it=iter([[output]])
        else:
            self.it=iter([[i] for i in output.split("\n")])
    def __iter__(self):
        return self
    def next(self):
        return self.it.next()
    def close(self):
        pass



class PipeVT:
    def __init__(self,envdict,largs,dictargs): #DO NOT DO ANYTHING HEAVY
        self.largs=largs
        self.envdict=envdict
        self.dictargs=dictargs
        self.names=['C1']
        self.linesplit=True
        if 'query' not in dictargs:
            raise functions.OperatorError(__name__.rsplit('.')[-1]," needs command argument ")
        self.query=dictargs['query']
        del dictargs['query']
        if 'lines' in dictargs and not dictargs['lines']:
            self.linesplit=False
    def getdescription(self):
        if not self.names:
            raise functions.OperatorError(__name__.rsplit('.')[-1],"VTable getdescription called before initiliazation")
        return [(i,) for i in self.names]
    def open(self):
        return PipeCursor(self.query,self.linesplit)
    def destroy(self):
        pass

boolargs=['lines']

def Source():
    return SourceVT(PipeVT,boolargs=boolargs,staticschema=True)



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