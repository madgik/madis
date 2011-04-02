"""
This is the jlist module

It features conversion to and from jlists

>>> create(3)
'3'
>>> create('test')
'test'
>>> create('[testjsonlike]')
3

"""

import json

def create(l):
    typel=type(l)
    if typel==list:
        lenl=len(l)
        if lenl==1:
            if type(l[0])==string:
                if len(l[0])==0:
                    return u''
                elif  l[0][0]!='[' or l[0][-1]!=']':
                    return l[0]
        if lenl==0:
            return ''
        return json.dumps(l)
    if typel==str:
        if len(l)==0:
            return u''
        elif l[0]!='[' or l[-1]!=']':
            return l
        else:
            return json.dumps(l)
    if typel==int:
        return json.dumps([l])

def createstrict(l):
    return json.dumps(l)

if __name__ == "__main__":
    import doctest
    doctest.testmod()
