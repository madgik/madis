"""
.. function:: xmlparse(root:None, xmlprototype, query:None)

    Parses an input xml stream. It starts parsing when it finds a root tag. An provided xml prototype fragment is used to create an schema, mapping from xml to a relational table.

:Returned table schema:
    Column names are named according to the schema of the provided xml prototype.

Examples:
    >>> table1('''
    ... '<a><b>row1val1</b></a>'
    ... '<a>'
    ... '<b>'
    ... 'row2val1</b><c><d>row2val</d></c>'
    ... '</a>'
    ... ''')
    >>> sql("select * from (xmlparse '<a><b>val1</b><c><d>val2</d></c></a>' select * from table1)")
    b        | c_d
    ------------------
    row1val1 |
    row2val1 | row2val

    >>> sql("select * from (xmlparse root:a '<t><a><b>val1</b><c><d>val2</d></c></a></t>' select * from table1)")
    b        | c_d
    ------------------
    row1val1 |
    row2val1 | row2val

    >>> table2('''
    ... '<a b="attrval1"><b>row1val1</b></a>'
    ... '<a>'
    ... '<b>'
    ... 'row2val1</b><c><d>row2val</d></c>'
    ... '</a>'
    ... ''')
    >>> sql("select * from (xmlparse '<a b=\\"v\\"><b>v</b><c><d>v</d></c></a>' select * from table2)")
    b        | b1       | c_d
    -----------------------------
    attrval1 | row1val1 |
             | row2val1 | row2val

"""
import vtiters
import functions
import xml.etree.cElementTree as etree

registered=True

def shorttag(t):
    if t[0] == '{':
        tag = t[1:].split("}")[1]
        return tag
    else:
        return t

def matchtag(a, b):
    if b[0] == '{':
        return a==b
    else:
        return shorttag(a)==b

def pathwithoutns(path):
    outpath=[]
    for i in path:
        if i[0]=="{":
            i=i.split('}')[1]
        elif ":" in i:
            i=i.split(':')[1]
        outpath+=[i]
    return "/".join(outpath)

class rowobj():
    def __init__(self, schema):
        self.schema=schema.schema
        self.row=['']*len(self.schema)

    def addtorow(self, xpath, data):
        fullattrib="/".join(xpath)

        shortattrib=pathwithoutns(xpath)

        if fullattrib in self.schema:
            attrib=fullattrib
        elif shortattrib in self.schema:
            attrib=shortattrib
        else:
            return

        if self.row[self.schema[attrib][0]]=='':
            self.row[self.schema[attrib][0]]=data
        else:
            i=1
            attribnum=attrib+str(i)
            while attribnum in self.schema:
                if self.row[self.schema[attribnum][0]]=='':
                    self.row[self.schema[attribnum][0]]=data
                    return
                i+=1
                attribnum=attrib+str(i)

    def resetrow(self):
        self.row=['']*len(self.schema)

class schemaobj():
    def __init__(self):
        self.schema={}
        self.colnames={}

    def addtoschema(self, path):
        fpath="/".join(path)
        if fpath not in self.schema:
            self.schema[fpath]=(len(self.schema), self.colname(path))
        else:
            fpath1=fpath
            i=1
            while True:
                fpath1=fpath+str(i)
                if fpath1 not in self.schema:
                    self.schema[fpath1]=(len(self.schema), self.colname(path))
                    break
                i=i+1

    def colname(self, path):
        sp=self.shortifypath(path)
        if sp not in self.colnames:
            self.colnames[sp]=0
            return sp
        else:
            self.colnames[sp]+=1
            return sp+str(self.colnames[sp])

    def shortifypath(self, path):
        outpath=[]
        for i in path:
            if i=='<atr>':
                continue
            if i[0]=="{":
                i=i.split('}')[1]
            elif ":" in i:
                i=i.split(':')[1]
            i="".join([x for x in i if x.lower() >="a" and x<="z"])
            outpath+=[i]
        return "_".join(outpath)


class XMLparse(vtiters.SchemaFromArgsVT):
    def __init__(self):
        self.schema=None
        self.subtreeroot=None
        self.rowobj=None
        self.query=None

    def getschema(self, *parsedArgs,**envars):
            s=schemaobj()

            opts=self.full_parse(parsedArgs)

            if 'root' in opts[1]:
                self.subtreeroot=opts[1]['root']

            try:
                self.query=opts[1]['query']
            except:
                raise functions.OperatorError(__name__.rsplit('.')[-1],"An input query should be provided as a parameter")

            xp=opts[0][0]

            xpath=[]
            capture=False

            import StringIO

            for ev, el in etree.iterparse(StringIO.StringIO(xp), ("start", "end")):
                if ev=="start":
                    if self.subtreeroot==None:
                        self.subtreeroot=el.tag
                    if capture:
                        xpath.append(el.tag)
                    if matchtag(el.tag, self.subtreeroot) and not capture:
                        capture=True
                    if capture and el.attrib!={}:
                        for k in el.attrib:
                            s.addtoschema(xpath+['<atr>', k])
                    continue

                if capture:
                    if el.text!=None and el.text.strip()!='':
                        s.addtoschema(xpath)
                    if ev=="end":
                        if el.tag==self.subtreeroot:
                            capture=False
                        if len(xpath)>0:
                            xpath.pop()

                if ev=="end":
                    el.clear()

            self.schema=s

            relschema=[None]*len(s.schema)

            for x,y in s.schema.itervalues():
                relschema[x]=(y, 'text')

            self.rowobj=rowobj(s)
            return relschema

    def open(self, *parsedArgs, **envars):
        class inputio():
            def __init__(self, connection, query):
                self.start=True
                self.qiter=connection.cursor().execute(query)

            def read(self,n):
                if self.start:
                    self.start=False
                    return "<xmlparce-forced-root-element>"
                return ''.join(self.qiter.next())

        etreeparse=iter(etree.iterparse(inputio(envars['db'], self.query), ("start", "end")))

        root=etreeparse.next()[1]
        capture=False
        schemaproc=2
        xpath=[]

        for ev, el in etreeparse:
            if ev=="start":
                root.clear()
                if capture:
                    xpath.append(el.tag)
                if matchtag(el.tag, self.subtreeroot) and not capture:
                    capture=True
                    if schemaproc==0: schemaproc=1
                if capture and el.attrib!={}:
                    if schemaproc==1:
                        for k,v in el.attrib.iteritems():
                            addtoschema("/".join(xpath+[k]), schema)
                    for k,v in el.attrib.iteritems():
                        self.rowobj.addtorow(xpath+['<atr>', k], v)
                continue

            if capture:
                if (el.text!=None):
                    if schemaproc==1:
                        addtoschema("/".join(xpath), schema)
                    self.rowobj.addtorow(xpath, el.text)

                if ev=="end":
                    if matchtag(el.tag,self.subtreeroot):
                        capture=False
                        yield self.rowobj.row
                        self.rowobj.resetrow()
                        if schemaproc==1:
                            schemaproc=2
                    if len(xpath)>0:
                        xpath.pop()

            if ev=="end":
                el.clear()


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
