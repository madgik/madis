"""
.. function:: xmlparse([root:None, strict:1, namespace:False, xmlprototype], query:None)

Parses an input xml stream. It starts parsing when it finds a root tag. A provided XML prototype fragment is used to create an schema, mapping from xml to a relational table.
If multiple values are found for the same tag in the input stream, then all values are returned separated with a tab (use tab-set operators to process them).

If no XML prototype is provided, then a jdict of the data is returned. In this case the *root* tag has to be provided. By default no namespace information is included in this mode.
To include the namespace information, the *namespace:1* or *ns:1* switch should also be provided.

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

    >>> sql('''select * from (xmlparse  '["a/@/b","a/b","a/c/d"]' select * from table2)''')
    b        | b1       | c_d
    -----------------------------
    attrval1 | row1val1 |
             | row2val1 | row2val

    >>> sql('''select * from (xmlparse  '{"a/b":[1,2] ,"a/c/d":1}' select * from table2)''')
    b        | b1 | c_d
    -----------------------
    row1val1 |    |
    row2val1 |    | row2val


    >>> sql("select * from (xmlparse root:a select * from table2)")
    C1
    -------------------------------------
    {"a/@/b":"attrval1","a/b":"row1val1"}
    {"a/b":"row2val1","a/c/d":"row2val"}

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
    Operator XMLPARSE: Undeclared path in xml-prototype was found in the input data. The path is:
    /b/@/np
    The data to insert into path was:
    np
    Last input line was:
    <b np="np">
    <BLANKLINE>

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
import collections
import json

try:
    import xml.etree.cElementTree as etree
except:
    import xml.etree.ElementTree as etree
import re

registered=True
cleandata=re.compile(r'[\n\r]*(.*?)\s*$', re.DOTALL| re.UNICODE)
attribguard='@'

# Workaround for older versions of elementtree
if not hasattr(etree, 'ParseError'):
    etree.ParseError=etree.XMLParserError

def matchtag(a, b):
    if b[0] == '{':
        return a == b
    else:
        if a[0] == '{':
            return a.split('}')[1] == b
        return a == b

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
        fullp='/'.join(xpath)

        path=None

        if fullp in self.schema:
            path=fullp
        else:
            shortp=pathwithoutns(xpath)
            if shortp in self.schema:
                path=shortp
        
        if path==None:
            if self.strict==2:
                path=xpath
                self.resetrow()
                msg='Undeclared path in xml-prototype was found in the input data. The path is:\n'
                shortp='/'+pathwithoutns(path)
                fullp='/'+'/'.join(path)
                if shortp!=fullp:
                    msg+=shortp+'\n'
                msg+=fullp+'\nThe data to insert into path was:\n'+functions.mstr(data)
                raise etree.ParseError(msg)
        else:
            if self.row[self.schema[path][0]]=='':
                self.row[self.schema[path][0]]=data.replace('\t', self.tabreplace)
                return

            i=1
            attribnum=path+'1'

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

class jdictrowobj():
    def __init__(self, ns, subtreeroot=None):
        self.rowdata=collections.OrderedDict()
        self.namespace=ns
        if subtreeroot!=None:
            self.root=[subtreeroot]
        else:
            self.root=[]
            
    def addtorow(self, xpath, data):
        if self.namespace:
            path='/'.join(self.root+xpath)
        else:
            path=pathwithoutns(self.root+xpath)

        if path not in self.rowdata:
            self.rowdata[path]=data
        else:
            if type(self.rowdata[path]) is list:
                self.rowdata[path].append(data)
            else:
                self.rowdata[path]=[self.rowdata[path], data]
            return
    
    @property
    def row(self):
        return [json.dumps(self.rowdata, separators=(',',':'), ensure_ascii=False)]

    def resetrow(self):
        self.rowdata=collections.OrderedDict()

class schemaobj():
    def __init__(self):
        self.schema={}
        self.colnames={}

    def addtoschema(self, path):
        fpath=cleandata.match("/".join(path)).groups()[0]
        if fpath=='':
            return

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
            if i==attribguard:
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
        self.namespace=False

    def getschema(self, *parsedArgs,**envars):
            s=schemaobj()

            opts=self.full_parse(parsedArgs)

            if 'root' in opts[1]:
                self.subtreeroot=opts[1]['root']

            if 'strict' in opts[1]:
                self.strict=int(opts[1]['strict'])

            if 'namespace' in opts[1] or 'ns' in opts[1]:
                self.namespace=True

            try:
                self.query=opts[1]['query']
            except:
                raise functions.OperatorError(__name__.rsplit('.')[-1],"An input query should be provided as a parameter")

            try:
                xp=opts[0][0]
            except:
                if self.subtreeroot==None:
                    raise functions.OperatorError(__name__.rsplit('.')[-1],"If no XML prototype is provided then at least a root should be provided")
                self.rowobj=jdictrowobj(self.namespace, self.subtreeroot)
                self.schema=None
                return [('C1', 'text')]

            try:
                jxp=json.loads(xp, object_pairs_hook=collections.OrderedDict)
            except ValueError:
                jxp=None

            if type(jxp) is list:
                for i in jxp:
                    path=i.split('/')
                    if self.subtreeroot==None:
                        self.subtreeroot=path[0]
                    if path[0]==self.subtreeroot:
                        path=path[1:]
                    s.addtoschema(path)
            elif type(jxp) is collections.OrderedDict:
                for k,v in jxp.iteritems():
                    path=k.split('/')
                    if self.subtreeroot==None:
                        self.subtreeroot=path[0]
                    if path[0]==self.subtreeroot:
                        path=path[1:]
                    if type(v) in (list, collections.OrderedDict):
                        for i in xrange(len(v)):
                            s.addtoschema(path)
                    else:
                        s.addtoschema(path)
            else:
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
                                s.addtoschema(xpath+[attribguard, k])
                        continue

                    if capture:
                        if el.text!=None and cleandata.match(el.text).groups()[0]!='':
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

            def read(self, n):
                
                def readline():
                    i=unicode(self.qiter.next()[0]).encode('utf-8')
                    return i

                if self.start:
                    self.start=False
                    self.lastline= readline()

                    if self.lastline.startswith('<?xml version='):
                        ll=self.lastline
                        while ll.find('?>')==-1:
                            ll+= readline()
                        self.lastline=ll
                        return ll.replace('?>','?>\n<xmlparce-forced-root-element>\n')
                    else:
                        return "<xmlparce-forced-root-element>\n"+self.lastline

                self.lastline= readline()
                if self.lastline.startswith('<?xml version='):
                    self.lastline= readline()
                return self.lastline


        rio=inputio(envars['db'], self.query)
        etreeended=False

        while not etreeended:
            etreeparse=iter(etree.iterparse(rio, ("start", "end")))
            capture=False
            xpath=[]
            addtorow=self.rowobj.addtorow
            resetrow=self.rowobj.resetrow
            lmatchtag=matchtag
            try:
                root=etreeparse.next()[1]

                for ev, el in etreeparse:
                    if ev=='start':
                        if capture:
                            xpath.append(el.tag)
                        else:
                            capture=lmatchtag(el.tag, self.subtreeroot)
                        if el.attrib!={} and capture:
                            for k,v in el.attrib.iteritems():
                                addtorow(xpath+[attribguard, k], v)
                    else: #if ev=='end':
                        if capture:
                            if el.text!=None:
                                eltext=el.text.strip()
                                if eltext!='':
                                    addtorow(xpath, eltext)
                            if lmatchtag(el.tag, self.subtreeroot):
                                root.clear()
                                capture=False
                                if self.strict>=0:
                                    yield self.rowobj.row
                                resetrow()

                            if len(xpath)>0:
                                xpath.pop()

                        el.clear()

                etreeended=True
            except etree.ParseError, e:
                rio.start=True
                resetrow()
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
