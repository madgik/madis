"""
.. function:: dirfiles()

:Returned table schema:
    Column C1 is absolute pathname
    Column C2 is filename

Examples:

    >>> sql("select c2 from dirfiles('.') where c2 like 'f%.py'")    # doctest:+ELLIPSIS +NORMALIZE_WHITESPACE
    c2
    -------
    file.py
    flow.py

"""
import os.path
import vtiters
import functions
import os

registered=True

class dirfiles(vtiters.StaticSchemaVT):
    def getschema(self):
        return [('c1', 'text'), ('c2', 'text')]

    def open(self, *parsedArgs, **envars):

        def expandedpath(p):
            return os.path.realpath(os.path.abspath(os.path.expanduser(os.path.expandvars(os.path.normcase(os.path.normpath(p))))))

        opts= self.full_parse(parsedArgs)

        dirname=None
        recursive=False

        if 'rec' in opts[1]:
            del opts[1]['rec']
            recursive=True

        if 'r' in opts[1]:
            del opts[1]['r']
            recursive=True

        if not recursive and len(opts[0])+len(opts[1])>1:
            if opt[0][0]=='rec' or opt[0][0]=='recursive':
                recursive=True
                del opts[0][0]

        if 'query' in opts[1]:
            dirname=query
        elif len(opts[0])>0:
            dirname=opts[0][-1]
        elif len(opts[0])==len(opts[1])==0:
            dirname='.'
        else:
            functions.OperatorError(__name__.rsplit('.')[-1], 'A directory name should be provided')

        dirname=expandedpath(dirname)

        if not recursive:
            for f in os.listdir(dirname):
                fullpathf=expandedpath(f)
                if os.path.isfile(fullpathf):
                    yield (expandedpath(f), f)

def Source():
    return vtiters.SourceCachefreeVT(dirfiles)


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
