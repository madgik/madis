import re
from unicodeops import unistr

def parse(args,boolargs=[],nonstringargs=dict(),needsescape=[]):
    listargs, keyargs= parametrize(*[unquote(unistr(a)) for a in args],**{'escapelists':needsescape})
    keyargsdict=translate(keyargs,boolargs,nonstringargs)
    return listargs, keyargsdict

def unescape(arg):
    arg=unistr(arg)
    q=arg.split("'")
    qlist=[]
    for qi in q:
        l=qi.split('\n')
        llist=[]
        for li in l:
            if li.endswith('\\'):
                llist+=[eval("'%s'" %(li.replace('\\','\\\\'))).replace('\\\\','\\') ]
            else:
                llist+=[eval("'%s'" %(li)) ]
        qlist+=['\n'.join(llist)]
    return "'".join(qlist)


def translate(dictargs,boolargs,nonstringargs):
    for key in dictargs:
        if key in boolargs:
            val = dictargs[key].lower()
            if val!='f' and val!='false' and val!='0':
                dictargs[key]=True
            else:
                dictargs[key]=False
        elif key in nonstringargs:
            val=dictargs[key]
            if dictargs[key] in nonstringargs[key]:
                dictargs[key]=nonstringargs[key][dictargs[key]]
            else:
                raise Exception("Argument parsing: Not valid value for argument '%s' " %(key))
    return dictargs




def unquote(p):
    if p.startswith("'") and p.endswith("'"):
        return p[1:-1].replace("''","'")
    elif p.startswith('"') and p.endswith('"'):
        return p[1:-1].replace('""','"')
    return p

re_params=re.compile(ur'^(?!\w:\\\w)(\w+):(.*)')


def parametrize(*args,**kargs):
    ps=[]
    kps=dict()
    escapelists=[]
    if 'escapelists' in kargs:
        escapelists=kargs['escapelists']
    for p in args:
        v=re_params.match(p)
        if not v:
            ps.append(p)
        else:
            if v.groups()[0] in escapelists:
                kps[str(v.groups()[0])]=unescape(v.groups()[1])
            else:
                kps[str(v.groups()[0])]=v.groups()[1]
    return ps,kps


