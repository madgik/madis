"""
.. function:: xmlparse(root:None, xmlprototype, query:None)

Parses an input xml stream. It starts parsing when it finds a root tag. An provided xml prototype fragment is used to create an schema, mapping from xml to a relational table.
If multiple values are found for the same tag in the input stream, then all values are returned separated with a tab (use tab-set operators to process them).

:'strict' option:

    - strict:2  ,if a failure occurs, the current transaction will be cancelled. Additionally if a tag isn't found in the xml prototype it will be regarded as failure.
    - strict:1  (default), if a failure occurs, the current transaction will be cancelled. Undeclared tags aren't regarded as failure.
    - strict:0  , returns all data that succesfully parses. The difference with strict 1, is that strict 0 tries to restart the xml-parsing after the failures and doesn't fail the transaction.
    - strict:-1 , returns all input lines in which the xml parser finds a problem. In essence this works as a negative xml parser.

:Returned table schema:
    Column names are named according to the schema of the provided xml prototype.

Examples:
    >>> table1('''
    ... '<a><b>row1val1</b><b>row1val1b</b><b>row1val1c</b></a>'
    ... '<a>'
    ... '<b>'
    ... 'row2val1</b><c><d>row2val</d></c>'
    ... '</a>'
    ... ''')
    >>> sql("select * from (xmlparse '<a><b>val1</b><b>val1</b><c><d>val2</d></c></a>' select * from table1)") # doctest: +NORMALIZE_WHITESPACE
    b        | b1                  | c_d
    ----------------------------------------
    row1val1 | row1val1b        row1val1c |
    row2val1 |                     | row2val

    >>> sql("select * from (xmlparse root:a '<t><a><b>val1</b><c><d>val2</d></c></a></t>' select * from table1)") # doctest: +NORMALIZE_WHITESPACE
    b                            | c_d
    --------------------------------------
    row1val1        row1val1b        row1val1c |
    row2val1                     | row2val

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

    >>> table2('''
    ... '<a b="attrval1"><b>row1val1</b></a>'
    ... '<a>'
    ... '</b>'
    ... 'row2val1</b><c><d>row2val</d></c>'
    ... '</a>'
    ... ''')
    >>> sql("select * from (xmlparse strict:0 '<a b=\\"v\\"><b>v</b><c><d>v</d></c></a>' select * from table2)")
    b        | b1       | c_d
    -------------------------
    attrval1 | row1val1 |

    >>> table3('''
    ... '<a><b>row1val1</b></a>'
    ... '<a>'
    ... '<b np="np">'
    ... 'row2val1</b><c><d>row2val</d></c>'
    ... '</a>'
    ... ''')
    >>> sql("select * from (xmlparse strict:2 '<a><b>val1</b><c><d>val2</d></c></a>' select * from table3)") #doctest:+ELLIPSIS +NORMALIZE_WHITESPACE
    Traceback (most recent call last):
    ...
    OperatorError: Madis SQLError:
    Operator XMLPARSE: Madis SQLError:
    Operator XMLPARSE: Undeclared tag in xml-prototype was found in the input data. The tag is:
    b/@/np
    Last input line was:
    <b np="np">

    >>> table4('''
    ... '<a><b>row1val1</b</a>'
    ... '<a><b>row1val1</b></a>'
    ... '<a><b np="np">row1val1</b></a>'
    ... '<a><b>row1val1</b></a>'
    ... '<a><b>row1val1</b</a>'
    ... ''')
    >>> sql("select * from (xmlparse strict:-1 '<a><b>val1</b><c><d>val2</d></c></a>' select * from table4)")
    C1
    ---------------------
    <a><b>row1val1</b</a>
    <a><b>row1val1</b</a>

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
    def __init__(self, schema, strictness):
        self.schema=schema.schema
        self.sobj=schema
        self.row=['']*len(self.schema)
        self.strict= strictness
        self.tabreplace='    '

    def addtorow(self, xpath, data):
        fullp="/".join(xpath)

        path=None

        if fullp in self.schema:
            path=fullp
        else:
            shortp=pathwithoutns(xpath)
            if shortp in self.schema:
                path=shortp
        
        if path==None:
            if self.strict==2:
                path=[]
                for i in xpath:
                    if i==self.sobj.attribguard:
                        i='@'
                    path.append(i)
                self.resetrow()
                raise functions.OperatorError(__name__.rsplit('.')[-1],'Undeclared tag in xml-prototype was found in the input data. The tag is:\n'+'/'.join(path))
        else:
            i=1
            attribnum=path+'1'

            if self.row[self.schema[path][0]]=='':
                self.row[self.schema[path][0]]=data.replace('\t', self.tabreplace)
                return
            
            oldattribnum=path
            while attribnum in self.schema:
                if self.row[self.schema[attribnum][0]]=='':
                    self.row[self.schema[attribnum][0]]=data.replace('\t', self.tabreplace)
                    return
                i+=1
                oldattribnum=attribnum
                attribnum=path+str(i)

            self.row[self.schema[oldattribnum][0]]+='\t'+data.replace('\t', self.tabreplace)


    def resetrow(self):
        self.row=['']*len(self.schema)

class schemaobj():
    def __init__(self):
        self.schema={}
        self.colnames={}
        self.attribguard='<at:r>'

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
            if i==self.attribguard:
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
        self.strict=1

    def getschema(self, *parsedArgs,**envars):
            s=schemaobj()

            opts=self.full_parse(parsedArgs)

            if 'root' in opts[1]:
                self.subtreeroot=opts[1]['root']

            if 'strict' in opts[1]:
                self.strict=int(opts[1]['strict'])

            try:
                self.query=opts[1]['query']
            except:
                raise functions.OperatorError(__name__.rsplit('.')[-1],"An input query should be provided as a parameter")

            try:
                xp=opts[0][0]
            except:
                raise functions.OperatorError(__name__.rsplit('.')[-1],"An XML prototype should be provided")

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
                            s.addtoschema(xpath+[s.attribguard, k])
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

            self.rowobj=rowobj(s, self.strict)
            if self.strict>=0:
                return relschema
            else:
                return [('C1', 'text')]

    def open(self, *parsedArgs, **envars):
        class inputio():

            def __init__(self, connection, query):
                self.lastline=''
                self.start=True
                self.qiter=connection.cursor().execute(query)

            def read(self,n):
                if self.start:
                    self.start=False
                    self.lastline=self.normalizeinput(self.qiter.next())
                    if self.lastline.startswith('<?xml version='):
                        return self.lastline.replace('?>','?>\n<xmlparce-forced-root-element>\n')
                    else:
                        return "<xmlparce-forced-root-element>\n"+self.lastline

                self.lastline=self.normalizeinput(self.qiter.next())
                if self.lastline.startswith('<?xml version='):
                    self.lastline=self.normalizeinput(self.qiter.next())
                return self.lastline

            def normalizeinput(self,i):
                i=''.join(i)
                if len(i)>0 and i[-1]=='\n':
                    return i
                else:
                    return i+'\n'


        rio=inputio(envars['db'], self.query)
        etreeended=False

        while not etreeended:
            etreeparse=iter(etree.iterparse(rio, ("start", "end")))

            root=etreeparse.next()[1]
                
            capture=False
            schemaproc=2
            xpath=[]
            try:

                for ev, el in etreeparse:
                    if ev=="start":
                        root.clear()
                        if capture:
                            xpath.append(el.tag)
                        if matchtag(el.tag, self.subtreeroot) and not capture:
                            capture=True
                            if schemaproc==0: schemaproc=1
                        if capture and el.attrib!={}:
    #                        if schemaproc==1:
    #                            for k,v in el.attrib.iteritems():
    #                                addtoschema("/".join(xpath+[k]), self.schema)
                            for k,v in el.attrib.iteritems():
                                self.rowobj.addtorow(xpath+[self.schema.attribguard, k], v)
                        continue

                    if capture:
                        if el.text!=None and el.text!='\n':
    #                        if schemaproc==1:
    #                            addtoschema("/".join(xpath), schema)
                            self.rowobj.addtorow(xpath, el.text)

                        if ev=="end":
                            if matchtag(el.tag,self.subtreeroot):
                                capture=False
                                if self.strict>=0:
                                    yield self.rowobj.row
                                self.rowobj.resetrow()
                                if schemaproc==1:
                                    schemaproc=2
                            if len(xpath)>0:
                                xpath.pop()

                    if ev=="end":
                        el.clear()

                etreeended=True
            except Exception,e:
#                if str(e).find('XML or text declaration')!=-1:
#                    rio.start=
                rio.start=True
                if self.strict>=1:
                    raise functions.OperatorError(__name__.rsplit('.')[-1], str(e)+'\n'+'Last input line was:\n'+rio.lastline)
                if self.strict==-1:
                    yield [rio.lastline]


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
