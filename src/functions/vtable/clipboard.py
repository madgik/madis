"""
.. function:: clipboard()

Returns the contents of the system's clipboard. If the clipboard's contents are guessed to be a table, then it automatically splits the contents in its output.

:h:
    if the 'h' option is provided to *clipboard()* function, the first row of the clipboard's data is regarded as the schema of the data.

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
        self.count = 0

    def getschema(self,samplerow):
        return self.schema

    def checkfordelimiter(self, delim = '\t'):
        #check for regular schema
        hasschema=True
        self.count=0
        if len(self.data)>0:
            self.count = self.data[0].count(delim)
            if self.count==0:
                hasschema=False
            else:
                for i in self.data[1:]:
                    if i.count(delim) != self.count:
                        hasschema=False
                        break
        return hasschema

    def open(self, *parsedArgs, **envars):
        import lib.pyperclip as clip
        data=unicode(clip.getcb(), 'utf_8')

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

        self.data = data

        hasschema = False
        if self.checkfordelimiter('\t'):
            delim = '\t'
            hasschema = True
        elif self.checkfordelimiter(','):
            delim = ','
            hasschema = True

        if hasschema:
            data=[i.split(delim) for i in data]
            self.schema = None
            header = False

            # Check for header directive
            for i in parsedArgs:
                if i.startswith('h'):
                    header = True

            if header and len(data)>0:
                self.schema = [(c,'text') for c in data[0]]
                data = data[1:]
            else:
                self.schema=[('C'+str(i),'text') for i in xrange(1, self.count+2)]

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
