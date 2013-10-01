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


import functions
import vtbase

import subprocess

registered=True

class PipeVT(vtbase.VT):
    def VTiter(self, *parsedArgs,**envars):
        largs, dictargs = self.full_parse(parsedArgs)

        if 'query' not in dictargs:
            raise functions.OperatorError(__name__.rsplit('.')[-1],"No command argument ")

        command=dictargs['query']
        
        linesplit=True
        if 'lines' in dictargs and dictargs['lines'][0] in ('f', 'F', '0'):
            linesplit=False

        yield (('C1', 'text'),)

        child=subprocess.Popen(command,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        output, error = child.communicate()
        if child.returncode!=0:
            raise functions.OperatorError(__name__.rsplit('.')[-1],"Command '%s' failed to execute because:\n%s" %(command,error.rstrip('\n\t ')))
        output=unicode(output,'utf-8')

        if not linesplit:
            yield [output]
        else:
            for i in output.split("\n"):
                yield [i]

def Source():
    return vtbase.VTGenerator(PipeVT)

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