"""
This is the jgroup module

It features conversion to and from jlists

>>> create(3)
3
>>> create('3')
'3'
>>> create('test')
'test'
>>> create('[testjsonlike]')
'["[testjsonlike]"]'
>>> create('[testjsonlike')
'[testjsonlike'
>>> create([3])
3
>>> create(['test'])
'test'
>>> create(['test',3])
'["test", 3]'
>>> create([3,'test'])
'[3, "test"]'
>>> create(['[test'])
'[test'

"""

import json

def create(l):
    typel=type(l)
    if typel==str:
        if l=='':
            return u''
        elif l[0]!='[' or l[-1]!=']':
            return l
        else:
            return json.dumps([l])
    if typel==int:
        return l
    if typel==list:
        lenl=len(l)
        if lenl==1:
            if type(l[0])==str:
                if l[0]=='':
                    return u''
                elif  l[0][0]!='[' or l[0][-1]!=']':
                    return l[0]
            if type(l[0])==int:
                return l[0]
        if lenl==0:
            return ''
        return json.dumps(l)


def createstrict(l):
    return json.dumps(l)

if __name__ == "__main__":
    import doctest
    doctest.testmod()
