"""
.. function:: examplevt(arguments)

A minimal example of a virtual table. Returns all the arguments passed to it.

:Returned table schema:
    Column names start from C1... , all column types are text

Examples:

    >>> sql("select * from examplevt(1, '2', 'var3')")    # doctest:+ELLIPSIS
    varname          | value
    -------------------------------------------------------------...
    parsedarg1       | 1
    parsedarg2       | 2
    parsedarg3       | var3
    envar:tablename  | vt_...
    envar:modulename | examplevt
    envar:db         | <functions.Connection object at 0x...>
    envar:dbname     | temp

    >>> sql("select * from (examplevt 'var1' 'var2' v1:test select 5)")    # doctest:+ELLIPSIS
    varname          | value
    -------------------------------------------------------...
    parsedarg1       | query:select 5
    parsedarg2       | var1
    parsedarg3       | var2
    parsedarg4       | v1:test
    envar:tablename  | vt_...
    envar:modulename | examplevt
    envar:db         | <functions.Connection object at 0x...>
    envar:dbname     | temp

"""
import vtiters

registered=True

class examplevt(vtiters.StaticSchemaVT):
    def getschema(self):
        return [('varname', 'text'), ('value', 'text')]

    def open(self, *parsedArgs, **envars):
        yield ["parsedargs", unicode(parsedArgs)]

        for x,y in envars.iteritems():
            yield ["envar:"+x, str(y)]

def Source():
    return vtiters.SourceCachefreeVT(examplevt)

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
