"""
.. function:: clipboard()

Returns the contents of the system's clipboard. If the clipboard's contents are guessed to be a table, then it automatically splits the contents in its output.

:Returned table schema:
    Column names start from C1... , all column types are text

Examples:

    >>> sql("select * from clipboard()")
    C1   | C2                    | C3          | C4
    ------------------------------------------------------
    1    | Zimbabwe              | 304.30      | 2009 est.
    2    | Japan                 | 192.10      | 2009 est.
    3    | Saint Kitts and Nevis | 185.00      | 2009 est.

"""
import vtiters

registered=True
external_stream=True

class clipboard(vtiters.SchemaFromSampleVT):
    def __init__(self):
        self.schema=[('C1', 'text')]

    def getschema(self,samplerow):
        return self.schema

    def open(self, **envars):
        import lib.pyperclip as clip
        data=clip.getcb()

        if data.count('\n')>=data.count('\r'):
            data=data.split('\n')
        else:
            data=data.split('\r')

        #delete empty lines from the end
        for i in xrange(len(data)-1,-1,-1):
            if len(data[i])==0:
                del data[i]
            else:
                break

        #check for regular schema
        hasschema=True
        count=0
        if len(data)>0:
            count=data[0].count('\t')
            if count==0:
                hasschema=False
            else:
                for i in data[1:]:
                    if i.count('\t')!=count:
                        hasschema=False
                        break

        if hasschema:
            self.schema=[('C'+str(i),'text') for i in xrange(1,count+2)]
            data=[i.split('\t') for i in data]
        else:
            data=[[r] for r in data]

        return iter(data)

def Source():
    return vtiters.SourceCachefreeVT(clipboard)


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
