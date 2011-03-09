"""
.. function:: clipboard()

    Returns the contents of the system's clipboard. If the clipboard's contents are guessed to be a table, then it automatically splits the contents in its output.

:Returned table schema:
    Column names start from C1... , all column types are text

Examples:

    >>> sql("select * from xmlparse('root:a', '<a><b>test</b><c><d>test1</d></c></a>')")
    C1   | C2                    | C3          | C4
    ------------------------------------------------------
    1    | Zimbabwe              | 304.30      | 2009 est.
    2    | Japan                 | 192.10      | 2009 est.
    3    | Saint Kitts and Nevis | 185.00      | 2009 est.

"""
import vtiters
import xml.etree.cElementTree as etree

registered=False

def shortifypath(path):
    outpath=[]
    for i in path:
        if i[0]=="{":
            i=i.split('}')[1]
        elif ":" in i:
            i=i.split(':')[1]
        i="".join([x for x in i if x.lower() >="a" and x<="z"])
        outpath+=[i]
    return "_".join(outpath)

def shorttag(t):
    if t[0] == "{":
        tag = t[1:].split("}")[1]
        return tag
    else:
        return t

class schemaobj():
    schema={}

    def addtoschema(self, path):
        attrib="/".join(path)
        if attrib not in self.schema:
            self.schema[attrib]=(len(self.schema), shortifypath(path))
        else:
            attrib1=attrib
            i=1
            while True:
                attrib1=attrib+str(i)
                if attrib1 not in self.schema:
                    self.schema[attrib1]=(len(self.schema), shortifypath(path)+str(i))
                    break
                i=i+1

class XMLparse(vtiters.SchemaFromArgsVT):
    def __init__(self):
        self.schema=None
        self.root=None

    def getschema(self, *parsedArgs,**envars):
            s=schemaobj()

            opts=self.full_parse(parsedArgs)

            self.root=opts[1]['root']

            xp=opts[0][0]

            print str(xp)

            events = "start", "end"
            root=None
            xpath=[]
            capture=False
            schemaproc=0

            import StringIO

            for ev, el in etree.iterparse(StringIO.StringIO(xp), events):

                if ev=="start":
                    if root==None:
                        root=el
                    if capture:
                        xpath.append(el.tag)
                    if shorttag(el.tag)==self.root and not capture:
                        capture=True
                        if schemaproc==0: schemaproc=1
                    if capture and el.attrib!={}:
                        if schemaproc==1:
                            for k in el.attrib:
                                s.addtoschema(xpath+[k])
                    root.clear()
                    continue

                if capture:
                    if (el.text!=None):
                        if schemaproc==1:
                            s.addtoschema(xpath)
                    if ev=="end":
                        if el.tag==self.root:
                            capture=False
                            if schemaproc==1:
                                schemaproc=2
                        if len(xpath)>0:
                            xpath.pop()

                if ev=="end":
                    el.clear()

            self.schema=s

            relschema=[None]*len(s.schema)

            for x,y in s.schema.itervalues():
                relschema[x]=y

            relschema=[(x, 'text') for x in relschema]

            return relschema

    def open(self, *parsedArgs, **envars):
        yield ['la', 'la1']

def Source():
    return vtiters.SourceCachefreeVT(XMLparse)


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
