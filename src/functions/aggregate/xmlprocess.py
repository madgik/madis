__docformat__ = 'reStructuredText en'
import xml.etree.cElementTree as etree
import Queue
import threading
import re
import functions

re_params=re.compile('(\w*):(.*)')

class schemaobj():
    def __init__(self):
        self.schema={}

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


class xmlproto:
    """
    .. function:: concatgroup(X)
    
    Concatenates strings in a group/dataset X.

    Example:

    >>> table1('''
    ... word1   1
    ... word2   1
    ... word3   2
    ... word4   2
    ... ''')
    >>> sql("select xmlproto(a, 'root:a') from (select '<a><b>t</b></a><a><c>t</c></a>' as a)")
    concatgroup(a)
    --------------
    word1word2
    word3word4
    """

    registered=False

    def __init__(self):
        self.input=None
        self.q=Queue.Queue(3)
        self.workerthr=threading.Thread(target=self.workerhandler)
        self.workerthr.start()
        self.mergedschema=schemaobj()
        self.init=True
        self.subroot=None
        self.exception=None

    def initargs(self, args):
        self.init=False
        for i in xrange(len(args)):
            v=re_params.match(args[i])
            if v is not None and v.groups()[0]!='' and v.groups()[1]!='' and i>0:
                v=v.groups()
                if v[0]=='root':
                    self.subroot=v[1]
        if self.subroot==None:
            self.q.put(None)
            raise functions.OperatorError('XMLPROTO',"Please specify a 'root:' parameter")
                    
    def step(self, *args):
        if self.init==True:
            self.initargs(args)

        self.q.put(args[0])
        if self.exception!=None:
            raise self.exception
        return

    def final(self):
        self.q.put(None)
        self.q.join()
        if self.exception!=None:
            raise self.exception
        return 'lala'

    def workerhandler(self):
        try:
            self.worker()
        except Exception,e:
            self.exception=e
            self.q.task_done()

    def worker(self):
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


        class inputio():
            def __init__(self, queue):
                self.q=queue
                self.start=True
                self.close=False

            def read(self,n):
                if self.start:
                    self.start=False
                    return "<xmlparce-forced-root-element>"
                if self.close:
                    return ''
                item=self.q.get(block=True)
                self.q.task_done()
                if item==None:
                    self.close=True
                    return '</xmlparce-forced-root-element>'
                return item

        etreeparse=iter(etree.iterparse(inputio(self.q), ("start", "end")))

        root=etreeparse.next()[1]
        xpath=[]
        capture=False

        s=schemaobj()

        for ev, el in etreeparse:
            if ev=="start":
                root.clear()
                if capture:
                    xpath.append(el.tag)
                if matchtag(el.tag, self.subroot) and not capture:
                    capture=True
                if capture and el.attrib!={}:
                    for k in el.attrib:
                        s.addtoschema(xpath+[k])
                continue

            if capture:
                if el.text!=None and el.text.strip()!='':
                    if capture:
                        s.addtoschema(xpath)
                if ev=="end":
                    if el.tag==self.subroot:
                        capture=False
                    if len(xpath)>0:
                        xpath.pop()

            if ev=="end":
                el.clear()


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
