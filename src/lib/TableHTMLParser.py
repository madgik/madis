from HTMLParser import *
import re

piencodingRegExp = '.*encoding=\"([^\"]+)\"'

metaencodingRegExp = '.*charset=([^\" ;]+)'

class TableHTMLParser(HTMLParser):
    "HTMLParser derived parser."

    bInspecting = True
    idle = 0
    intable = 1
    inheader = 2
    inraw = 3
    incolumn = 4
    state = idle
    tablesFound = 0

    def __init__(self, tableNum):
        "Initialise an object, passing 'verbose' to the superclass."
        HTMLParser.__init__(self)
        self.line = []
        self.lines = []
        self.header=[]
        self.value=''
        self.tableNum = tableNum
        self.encoding = 'utf-8'

    def close(self):
        self.f.close()


    def parse(self, s):
        "Parse the given string 's'."
        #print s
        self.lines = []
        self.feed(unicode(s,self.encoding))
        for el in self.lines:
            yield el
    def handle_pi(self,data):

        lst=re.findall(piencodingRegExp,data)
        if len(lst):
            self.encoding=lst[0]

    def handle_data(self, data):
        "Handle arbitrary data"
        if self.state == self.incolumn and self.bInspecting == False:
            self.value += data

    def handle_starttag(self, tag, attrs):
        dattrs=dict(attrs)
        if tag=='meta':
            if 'content' in dattrs:
                lst=re.findall(metaencodingRegExp,dattrs['content'])
                if len(lst):
                    self.encoding=lst[0]

        if tag == "table":
            self.tablesFound += 1
            self.state = self.intable
            if self.tablesFound == self.tableNum:
                self.bInspecting = False # table found
            else: self.bInspecting = True
        elif tag == "th":
            if 'colspan' in dattrs:
                self.replicate=int(dattrs['colspan'])
            else:
                self.replicate=0
            self.state = self.incolumn
            self.value=''
            
        elif tag == "tr":
            self.line = [] # init line
            self.header = []
            self.state = self.inraw
        elif tag == "td":
            if 'colspan' in dattrs:
                self.replicate=int(dattrs['colspan'])
            else:
                self.replicate=0
            self.value=''
            self.state = self.incolumn

    def handle_endtag(self, tag):
        if tag == 'table':
            self.state = self.idle
            self.bInspecting = True
        elif tag == "th":
            if self.bInspecting == False:
                if self.replicate:                    
                    self.header+=[self.value+str(i) for i in range(1,self.replicate+1)]
                else:
                    self.header+=[self.value]
            self.state = self.inraw
        elif tag == "tr" and self.bInspecting == False:
            if self.header!=[]:
                self.lines+=[tuple(self.header)]
            else:
                self.lines+=[self.line]
            self.line=[]
            self.header=[]
            self.state = self.intable
        elif tag == "td":
            if self.bInspecting == False:
                self.line+=[self.value]*(self.replicate+1)
            self.state = self.inraw
