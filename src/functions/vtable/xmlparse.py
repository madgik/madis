"""
.. function:: xmlparse([root:None, strict:1, namespace:False, xmlprototype], query:None)

Parses an input xml stream. It starts parsing when it finds a root tag. A provided XML prototype fragment is used to create an schema, mapping from xml to a relational table.
If multiple values are found for the same tag in the input stream, then all values are returned separated with a tab (use tab-set operators to process them).

If no XML prototype is provided, then a jdict of the data is returned. In this case the *root* tag has to be provided. By default no namespace information is included in this mode.
To include the namespace information, the *namespace:1* or *ns:1* switch should also be provided.

:XML prototype:

    XML prototype may be:

    - a fragment of XML which will be matched with the input data.
    - a jpack.
    - a jdict.
        
    If a the characters **"*"** or **"$"** are provided as a value of any of these prototypes, then a full XML subtree of a path will be returned in the resulting data.

:'namespace' or 'ns' option:

    Include namespace information in the returned jdicts.

:'fast' option:

    Read input data in bulk. For some XML input files (having lots of small line lengths), it can speed up XML processing by up to 30%. The downside of this option, is that when an error
    occurs no last line information is returned, so use this option only when you are sure that the XML input is well formed.

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
    ... 'row2val1</b><c>asdf<d>row2val</d></c>'
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

    >>> sql('''select * from (xmlparse  '{"a/b":[1,2] ,"a/c":[1,"*"]}' select * from table2)''')
    b        | b1 | c    | c_$
    -------------------------------------
    row1val1 |    |      |
    row2val1 |    | asdf | <d>row2val</d>

    >>> sql('''select * from (xmlparse  '["a/b", "a/c", "a/c/*"]' select * from table2)''')
    b        | c    | c_$
    --------------------------------
    row1val1 |      |
    row2val1 | asdf | <d>row2val</d>

    >>> sql("select * from (xmlparse '<a><b>v</b><c>*</c></a>' select * from table2)")
    b        | c_$
    -------------------------
    row1val1 |
    row2val1 | <d>row2val</d>

    >>> sql("select * from (xmlparse root:a select * from table2)")
    C1
    -------------------------------------------------
    {"a/@/b":"attrval1","a/b":"row1val1"}
    {"a/b":"row2val1","a/c/d":"row2val","a/c":"asdf"}

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
    Operator XMLPARSE: Undeclared path in XML-prototype was found in the input data. The path is:
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
    ----------------------
    <a><b>row1val1</b</a>
    <a><b>row1val1</b</a>

"""
import vtiters
import functions
import collections
import htmlentitydefs
import json
import cStringIO as StringIO

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

def unescape(text):
    def fixup(m):
        text = m.group(0)
        if text=='&amp;': return text
        if text[:2] == "&#":
            # character reference
            try:
                if text[:3] == "&#x":
                    return unichr(int(text[3:-1], 16))
                else:
                    return unichr(int(text[2:-1]))
            except ValueError:
                pass
        else:
            # named entity
            try:
                text = unichr(htmlentitydefs.name2codepoint[text[1:-1]])
            except KeyError:
                pass
        print text
        return text # leave as is
    return re.sub("&#?\w+;", fixup, text)

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
        self.schemagetall=schema.getall
        self.sobj=schema
        self.schemacolsnum=len(schema.schema)+len(schema.getall)
        self.row=['']*self.schemacolsnum
        self.strict= strictness
        self.tabreplace='    '
        self.addtorowall=self.addtorow

    def addtorow(self, xpath, data, elem=None):
        if elem!=None:
            if self.schemagetall=={}:
                return
            s=self.schemagetall
            data=etree.tostring(elem)
        else:
            s=self.schema

        fullp='/'.join(xpath)

        path=None

        if fullp in s:
            path=fullp
        else:
            shortp=pathwithoutns(xpath)
            if shortp in s:
                path=shortp
        
        if path==None:
            if self.strict==2 and elem==None:
                path=xpath
                self.resetrow()
                msg='Undeclared path in XML-prototype was found in the input data. The path is:\n'
                shortp='/'+pathwithoutns(path)
                fullp='/'+'/'.join(path)
                if shortp!=fullp:
                    msg+=shortp+'\n'
                msg+=fullp+'\nThe data to insert into path was:\n'+functions.mstr(data)
                raise etree.ParseError(msg)
        else:
            if self.row[s[path][0]]=='':
                self.row[s[path][0]]=data.replace('\t', self.tabreplace)
                return

            i=1
            attribnum=path+'1'

            oldattribnum=path
            while attribnum in s:
                if self.row[s[attribnum][0]]=='':
                    self.row[s[attribnum][0]]=data.replace('\t', self.tabreplace)
                    return
                i+=1
                oldattribnum=attribnum
                attribnum=path+str(i)

            self.row[s[oldattribnum][0]]+='\t'+data.replace('\t', self.tabreplace)

    def resetrow(self):
        self.row=['']*self.schemacolsnum

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

    def addtorowall(self, xpath, data, elem):
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
        self.getall={}

    def addtoschema(self, path):
        s=self.schema
        pathpostfix=[]
        if path!=[] and path[-1] in ('*', '$'):
            path=path[0:-1]
            s=self.getall
            pathpostfix=['$']

        fpath=cleandata.match("/".join(path)).groups()[0].lower()
        if fpath=='':
            return

        if fpath not in s:
            s[fpath]=(len(self.schema)+len(self.getall), self.colname(path+pathpostfix))
        else:
            fpath1=fpath
            i=1
            while True:
                fpath1=fpath+str(i)
                if fpath1 not in s:
                    s[fpath1]=(len(self.schema)+len(self.getall), self.colname(path+pathpostfix))
                    break
                i=i+1

    def colname(self, path):
        sp=self.shortifypath(path).lower()
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
            i="".join([x for x in i if x=='$' or (x.lower()>="a" and x<="z")])
            outpath+=[i]
        return "_".join(outpath)

    def getrelschema(self):
        relschema=[None]*(len(self.schema)+len(self.getall))

        for x,y in self.schema.itervalues():
            relschema[x]=(y, 'text')

        for x,y in self.getall.itervalues():
            relschema[x]=(y, 'text')

        return relschema


class XMLparse(vtiters.SchemaFromArgsVT):
    def __init__(self):
        self.schema=None
        self.subtreeroot=None
        self.rowobj=None
        self.query=None
        self.strict=1
        self.namespace=False
        self.fast=False

    def getschema(self, *parsedArgs,**envars):
            s=schemaobj()

            opts=self.full_parse(parsedArgs)

            if 'root' in opts[1]:
                self.subtreeroot=opts[1]['root']

            if 'strict' in opts[1]:
                self.strict=int(opts[1]['strict'])

            if 'namespace' in opts[1] or 'ns' in opts[1]:
                self.namespace=True

            if 'fast' in opts[1]:
                self.fast=True

            try:
                self.query=opts[1]['query']
            except:
                raise functions.OperatorError(__name__.rsplit('.')[-1],"An input query should be provided as a parameter")

            try:
                xp=opts[0][0]
            except:
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
                        for i in v:
                            if i in ('*', '$'):
                                s.addtoschema(path+['*'])
                            else:
                                s.addtoschema(path)
                    else:
                        if v in ('*', '$'):
                            s.addtoschema(path+['*'])
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
                            if el.text.strip() in ('$', '*'):
                                s.addtoschema(xpath+['*'])
                            else:
                                s.addtoschema(xpath)
                        if ev=="end":
                            if el.tag==self.subtreeroot:
                                capture=False
                            if len(xpath)>0:
                                xpath.pop()

                    if ev=="end":
                        el.clear()

            relschema=s.getrelschema()
            
            if relschema==[]:
                raise functions.OperatorError(__name__.rsplit('.')[-1], 'No input schema found')

            self.rowobj=rowobj(s, self.strict)
            if self.strict>=0:
                return s.getrelschema()
            else:
                return [('C1', 'text')]

    def open(self, *parsedArgs, **envars):

        class inputio():
            def __init__(self, connection, query, fast=False):
                self.lastline=''
                self.read=self.readstart
                self.qiter=connection.cursor().execute(query)
                self.fast=fast
                self.insertedforcedroot=False

            def restart(self):
                self.insertedforcedroot=False
                self.read=self.readstart

            def readstart(self, n):
                
                def readline():
                    i=self.qiter.next()[0].encode('utf-8')
                    if i.endswith('\n'):
                        return i
                    else:
                        return i+'\n'

                self.lastline= readline()
                
                rline=self.lastline.strip()

                if not (rline.startswith('<?xml version=') or rline.startswith('<!DOCTYPE')):
                    if self.fast:
                        self.read=self.readtailfast
                    else:
                        self.read=self.readtail

                if rline.startswith('<?xml version='):
                    ll=self.lastline
                    while ll.find('?>')==-1:
                        ll+= readline()
                    self.lastline=ll
                    if self.insertedforcedroot:
                        return ll
                    else:
                        self.insertedforcedroot=True
                        return ll.replace('?>','?>\n<xmlparce-forced-root-element>\n')
                elif rline.startswith('<!DOCTYPE'):
                    ll=self.lastline
                    while ll.find('>')==-1:
                        ll+= readline()
                    self.lastline=ll
                    if self.insertedforcedroot:
                        return re.sub(r'[^>]+>','', ll, 1)
                    else:
                        self.insertedforcedroot=True
                        return re.sub(r'[^>]+>','<xmlparce-forced-root-element>\n', ll, 1)
                else:
                    if self.insertedforcedroot:
                        return self.lastline
                    else:
                        return "<xmlparce-forced-root-element>\n"+self.lastline

            def readtail(self, n):
                line= unescape(self.qiter.next()[0]).encode('utf-8')
                if line.startswith('<?xml version='):
                    line= self.qiter.next()[0].encode('utf-8')
                if not line.endswith('\n'):
                    line+='\n'
                self.lastline=line
                return line

            def readtailfast(self, n):
                buffer=StringIO.StringIO()
                try:
                    while buffer.tell()<n:
                        line= self.qiter.next()[0].encode('utf-8')
                        if line.startswith('<?xml version='):
                            line= self.qiter.next()[0].encode('utf-8')
                        if line.endswith('\n'):
                            buffer.write(line)
                        else:
                            buffer.writelines((line,'\n'))
                except StopIteration:
                    if buffer.tell()==0:
                        raise StopIteration
                return buffer.getvalue()

            def close(self):
                self.qiter.close()

        rio=inputio(envars['db'], self.query, self.fast)
        etreeended=False

        try:
            while not etreeended:
                etreeparse=iter(etree.iterparse(rio, ("start", "end")))
                capture=False
                xpath=[]
                addtorow=self.rowobj.addtorow
                addtorowall=self.rowobj.addtorowall
                resetrow=self.rowobj.resetrow
                if self.subtreeroot==None:
                    lmatchtag=lambda x,y:True
                else:
                    lmatchtag=matchtag
                try:
                    root=etreeparse.next()[1]

                    for ev, el in etreeparse:
                        if ev=='start':
                            if capture:
                                addtorowall(xpath, '', el)
                                xpath.append(el.tag.lower())
                            else:
                                capture=lmatchtag(el.tag, self.subtreeroot)
                            if el.attrib!={} and capture:
                                for k,v in el.attrib.iteritems():
                                    addtorow(xpath+[attribguard, k.lower()], v)
                        else:
                            if capture:
                                if el.text!=None:
                                    eltext=el.text.strip()
                                    if eltext!='':
                                        addtorow(xpath, eltext)
                                if lmatchtag(el.tag, self.subtreeroot):
                                    root.clear()
                                    if self.subtreeroot!=None:
                                        capture=False
                                    if self.strict>=0:
                                        yield self.rowobj.row
                                    resetrow()

                                if len(xpath)>0:
                                    xpath.pop()

                            el.clear()

                    etreeended=True
                except etree.ParseError, e:
                    rio.restart()
                    resetrow()
                    if self.strict>=1:
                        raise functions.OperatorError(__name__.rsplit('.')[-1], str(e)+'\n'+'Last input line was:\n'+rio.lastline)
                    if self.strict==-1:
                        yield [rio.lastline]
        finally:
            rio.close()


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
