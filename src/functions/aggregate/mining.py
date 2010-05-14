import re
import itertools
import setpath
import functions
from lib.buffer import CompBuffer

__docformat__ = 'reStructuredText en'

re_params=re.compile('(\w*):(.*)')

def consumer(func):
    """A decorator, advances func to its first yield point when called.
    """

    from functools import wraps

    @wraps(func)
    def wrapper(*args,**kw):
        gen = func(*args, **kw)
        gen.next()
        return gen
    return wrapper


class freqitemsets:
    """
    .. function:: freqitemsets(datacol, [threshold, noautothres, stats, maxlen]) -> [itemset_id:int, itemset_length:int, itemset_frequency:int, item:text]

    Calculates frequent itemsets on a given column (datacol). The algorithm is tuned for the
    case when we have many different items (in the order of millions), many input itemsets, but
    small itemset length (10-20).

    Returned table schema:

    :itemset_id: Automatic itemset id
    :itemset_length: Length of itemset
    :itemset_frequency: How many times an itemset has been found
    :item: Itemset's item value

    Parameters:

    :datacol:

        Column on which to calculate frequent itemsets

    :threshold: Default is 2

        How many times an freq. itemset must appear for it to appear in the results

    :noautothres: 1/0 (Default is 0)

        Do not calculate the threshold automatically

    :stats: 1/0 (Default is 0)

        Return frequent itemset statistics

    :maxlen: 1-inf (Default is inf)

        Maximum itemset length to search

    Examples:
    
    >>> table1('''
    ... 'car wood bike' 'first group'
    ... 'car car wood'  'first group'
    ... 'car wood'      'first group'
    ... 'car wood ice'  'first group'
    ... 'ice'           'second group'
    ... 'car ice'       'second group'
    ... 'car cream' 'second group'
    ... 'icecream ice car'  'second group'
    ... ''')
    >>> sql("select b,freqitemsets(a, 'threshold:2', 'noautothres:1', 'maxlen:2') from table1 group by b")
    b            | itemset_id | itemset_length | itemset_frequency | item
    ---------------------------------------------------------------------
    first group  | 1          | 1              | 4                 | wood
    first group  | 2          | 1              | 4                 | car
    first group  | 3          | 2              | 4                 | car
    first group  | 3          | 2              | 4                 | wood
    second group | 1          | 1              | 3                 | ice
    second group | 2          | 1              | 3                 | car
    second group | 3          | 2              | 2                 | car
    second group | 3          | 2              | 2                 | ice
    """


    registered=True
    multiset=True

    def __init__(self):
        self.threshold=2
        self.startingthreshold=2
        self.autothres=1
        self.compress=0
        self.initstatic=False
        self.input={}
        self.maxlength=0
        self.kwcode={}
        self.codekw={}
        self.maxkwcode=0
        self.overthres={}
        self.belowthres={}
        self.passedkw={}
        self.init=True
        self.outbuf= CompBuffer()
        self.itemset_id=0
        self.maxlen=None
        self.stats=False

    def initargs(self, args):
        self.init=False
        for i in xrange(len(args)):
            v=re_params.match(args[i])
            if v is not None and v.groups()[0]!='' and v.groups()[1]!='' and i>0:
                v=v.groups()
                if v[0]=='threshold':
                    try:
                        self.threshold=int(v[1])
                        self.startingthreshold=self.threshold
                    except:
                        raise functions.OperatorError("FreqItemsets",'No integer value given for threshold')
                if v[0]=='noautothres':
                    self.autothres=0
                if v[0]=='compress':
                    self.compress=1
                if v[0]=='maxlen':
                    self.maxlen=int(v[1])
                if v[0]=='stats':
                    self.stats=True

    def demultiplex(self,data):
        iterable=None
        iterpos=-1

        for i in xrange(len(data)):
            if hasattr(data[i],'__iter__')==True:
                iterable=data[i]
                iterpos=i
                break

        if iterpos==-1:
            yield list(data)
        else:
            pre=list(data[0:iterpos])
            post=list(data[iterpos+1:])
            for i in iterable:
                if hasattr(i,'__iter__')==False:
                    yield pre+[i]+post
                else:
                    yield pre+list(i)+post

    def save(self,data):
        from operator import itemgetter

        for its,v in sorted(data.items(), key=itemgetter(1),reverse=True):
            self.itemset_id+=1
            for i in self.demultiplex( (self.itemset_id, len([self.codekw[i] for i in its]), v, [self.codekw[i] for i in its]) ):
                self.outbuf.write( i )
        
    def insertcombfreq(self, comb, freq):
        if comb in self.overthres:
            self.overthres[comb]+=freq
        else:
            if comb in self.belowthres:
                self.belowthres[comb]+=freq
            else:
                self.belowthres[comb]=freq

            if self.belowthres[comb]>=self.threshold:
                self.overthres[comb]=self.belowthres[comb]
                del(self.belowthres[comb])
                for k in comb:
                    if self.compress==0:
                        self.passedkw[k]=True
                    elif not k in self.passedkw:
                        self.passedkw[k]=self.overthres[comb]
                    else:
                        self.passedkw[k]+=self.overthres[comb]

    def insertitemset(self, itemset):
        if itemset not in self.input:
            self.input[itemset]=1
        else:
            self.input[itemset]+=1

    def cleanitemsets(self, minlength):
        newitemsets={}
        for k,v in self.input.iteritems():
            itemset=tuple([i for i in k if i in self.passedkw])
            if self.compress==1:
                esoteric_itemset=tuple([i for i in itemset if self.passedkw[i]==v])
                if len(esoteric_itemset)>0:
                    if len(itemset)>=minlength:
                        self.overthres[itemset]=v
                    itemset=tuple([i for i in itemset if self.passedkw[i]!=v])
            if len(itemset)>=minlength:
                if itemset not in newitemsets:
                    newitemsets[itemset]=v
                else:
                    newitemsets[itemset]+=v

        self.input=newitemsets

    def step(self, *args):
        if self.init==True:
            self.initargs(args)

        if len(args[0])==0:
            return
        
        itms=sorted(set(args[0].split(' ')))
        itms=[x for x in itms if x!='']
        li=len(itms)
        if li>0:
            if li>self.maxlength:
                self.maxlength=li

            inputkws=[]
            for kw in itms:
                if len(kw)==0:
                    print itms, args[0], len(args[0]), li
                if kw not in self.kwcode:
                    self.kwcode[kw]=self.maxkwcode
                    self.codekw[self.maxkwcode]=kw
                    inputkws.append(self.maxkwcode)
                    self.insertcombfreq( (self.maxkwcode,),1 )
                    self.maxkwcode+=1
                else:
                    itm=self.kwcode[kw]
                    self.insertcombfreq( (itm,),1 )
                    inputkws.append(itm)

            if len(inputkws)>1:
                self.insertitemset(tuple(inputkws))

    def final(self):
        self.outbuf.writeheader(['itemset_id', 'itemset_length', 'itemset_frequency', 'item'])
        statsstr=''
        statsstr+='Max transaction length:'+ str(self.maxlength)+'\n'
        #print "input:", self.input
        splist=[{},{}]
        del(self.kwcode)
        splist[1]=self.overthres
        statsstr+='1|'+"# of combinations:"+str(len(splist[1]))+'|'+"# of passed transactions:"+ str(len(self.input))+'|'+ "# of valid keywords:"+ str(len(self.passedkw))+'\n'

        if self.maxlen==None:
            self.maxlen=self.maxlength
        for l in xrange(2, min(self.maxlength+1, self.maxlen+1)):
            splist.append({})
            self.belowthres={}
            self.overthres={}
            prevl=l-1

            # Autothresholding
            if self.autothres==1:
                if len(self.input)==0 or len(self.passedkw)==0:
                    break
                else:
                    self.threshold=self.startingthreshold + int(len(self.passedkw)/len(self.input))

            self.cleanitemsets(l)
            self.passedkw={}

            for k,v in self.input.iteritems():
                for k in itertools.combinations(k,l):
                    insertit=True
                    for i1 in itertools.combinations(k, prevl):
                        if not splist[prevl].has_key(i1):
                            insertit=False
                            break

                    if insertit:
                        self.insertcombfreq( k,v )

            splist[l]=self.overthres
            statsstr+=str(l)+'|'+"# of combinations:"+str(len(splist[l]))+'|'+"# of passed transactions:"+ str(len(self.input))+'|'+ "# of valid keywords:"+str(len(self.passedkw))+'\n'

            if not self.stats:
                self.save(splist[prevl])
            splist[l-1]={}

        if not self.stats:
            self.save(splist[-1])
        splist[-1]={}

        del(self.overthres)
        del(self.belowthres)
        del(self.passedkw)
        del(self.input)
        del(self.codekw)
        del(splist)

        if self.stats:
            return statsstr
        else:
            return self.outbuf.serialize()


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

