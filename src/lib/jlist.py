"""
This is the jgroup module

It features conversion to and from jlists

>>> toj(3)
3
>>> toj('3')
'3'
>>> toj('test')
'test'
>>> toj(u'test')
u'test'
>>> toj('[testjsonlike]')
'["[testjsonlike]"]'
>>> toj('[testjsonlike')
'[testjsonlike'
>>> toj([3])
3
>>> toj(['test'])
'test'
>>> toj(['test',3])
'["test", 3]'
>>> toj([3,'test'])
'[3, "test"]'
>>> toj(['[test'])
'[test'
>>> toj(None)
'[null]'
>>> toj('')
u''
>>> toj([])
u'[]'
>>> tojstrict('asdf')
'["asdf"]'
>>> tojstrict(['a',3])
'["a", 3]'
>>> fromj('["a", 3]')
[u'a', 3]
>>> fromj(3)
[3]
>>> fromj('a')
['a']
>>> fromj('["a", 3]')
[u'a', 3]
>>> fromj('[null]')
[None]
>>> fromj('[asdf]')
['[asdf]']
>>> fromj('')
[u'']
>>> fromj('[]')
[]
"""

import json

def toj(l):
    if l==None:
        return '[null]'
    typel=type(l)
    if typel==str or typel==unicode:
        if l=='':
            return u''
        elif l[0]!='[' or l[-1]!=']':
            return l
        else:
            return json.dumps([l])
    if typel==int or typel==float:
        return l
    if typel==list or typel==tuple:
        lenl=len(l)
        if lenl==1:
            typel=type(l[0])
            if typel==str or typel==unicode:
                if l[0]=='':
                    return u''
                elif  l[0][0]!='[' or l[0][-1]!=']':
                    return l[0]
            if typel==int or typel==float:
                return l[0]
        if lenl==0:
            return u'[]'
        return json.dumps(l)

def tojstrict(l):
    if type(l)==list:
        return json.dumps(l)
    return json.dumps([l])

def fromj(j):
    typej=type(j)
    if typej==int or typej==float:
        return [j]
    if typej==str or typej==unicode:
        if j=='':
            return [u'']
        if j[0]=='[' and j[-1]==']':
            try:
                return json.loads(j)
            except:
                return [j]
        return [j]

def flatten(l, ltypes=(list, tuple)):
    ltype = type(l)
    l = list(l)
    i = 0
    while i < len(l):
        while isinstance(l[i], ltypes):
            if not l[i]:
                l.pop(i)
                i -= 1
                break
            else:
                l[i:i + 1] = l[i]
        i += 1
    return ltype(l)

if __name__ == "__main__":
    import doctest
    doctest.testmod()
