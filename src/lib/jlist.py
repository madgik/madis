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
'test'
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
>>> fromj('["a", 3]', 'b')
[u'a', 3, 'b']
>>> fromj('["a", 3]', 'b', 3, '["a", 3]')
[u'a', 3, 'b', 3, u'a', 3]
"""

import json

def toj(l):
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
    if typel==list:
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
            return ''
        return json.dumps(l)

def tojstrict(l):
    if type(l)==list:
        return json.dumps(l)
    return json.dumps([l])

def fromj(*jl):
    jout=[]
    for j in jl:
        typej= type(j)
        if typej==int or typej==float:
            jout+= [j]
            continue
        if typej==str or typej==unicode:
            if j=='':
                continue
            if j[0]=='[' and j[-1]==']':
                jout+= json.loads(j)
                continue
            jout+= [j]
    return jout

if __name__ == "__main__":
    import doctest
    doctest.testmod()
