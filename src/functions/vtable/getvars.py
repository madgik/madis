"""
.. function:: getvars()

Returns the defined variables with their values.

:Returned table schema:
    - *variable* text
        Variable name.
    - *value* text
        Variable value

.. toadd See also variables.. LINK ???

Examples:


    >>> sql("var 'env' 'testing' ")
    var('env','testing')
    --------------------
    testing
    >>> sql("getvars")
    variable | value
    -------------------
    flowname |
    execdb   | :memory:
    env      | testing


"""


from vtiterable import SourceVT
import functions
registered=True

class GetVarsCursor:
    def __init__(self,list):
        self.iter=iter(list)
    def next(self):
        return self.iter.next()
    def __iter__(self):
        return self
    def close(self):
        pass
class GetVarsVT:
    def __init__(self,envdict,largs,dictargs): #DO NOT DO ANYTHING HEAVY
        self.largs=largs
        self.envdict=envdict
        self.dictargs=dictargs
    def getdescription(self):
        return [('variable',),('value',)]
    def open(self):
        return GetVarsCursor([[i,functions.variables.__dict__[i]] for i in functions.variables.__dict__])
    def disconnect(self):
        pass
    def destroy(self):
        pass

def Source():
    return SourceVT(GetVarsVT)



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