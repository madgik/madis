"""
.. function:: output(query:None,file, [formatting options])

Writes in *file* the output of *query* formatted according to *formatting* options.

:Returned table schema:
    - *return_value* int
        Boolean value 1 indicating success. On failure an exception is thrown.

Formatting options:

.. toadd html        In html mode table is formatted as an html table TODO ????

:mode:
    - gtable      In gtable mode table is formatted as a google Data Table for visualisation
    - gjson       In gjson mode table is formatted as true json in accepted google Data Table for visualisation json schema
    - csv        Default value, in csv mode table is formatted in csv, many csv settings available
    - plain      The columns are concatened and written, after each row a new line is added.

    If *mode* is not *csv* any given csv formatting options are ignored

:append:
                    t/f If true the output is append in the file, ignored in compression mode

Detailed description of additional output formating options can be found in :func:`~functions.vtable.file.file` function description.

Examples:

    >>> table1('''
    ... James   10	2
    ... Mark    7	3
    ... Lila    74	1
    ... ''')
    >>> sql("select * from table1")
    a     | b  | c
    --------------
    James | 10 | 2
    Mark  | 7  | 3
    Lila  | 74 | 1
    >>> sql("output file:../../tests/table1.csv delimiter:# header:t select a as name , b as age, c as rank from table1")
    return_value
    ------------
    1
    >>> sql("file file:../../tests/table1.csv delimiter:# header:t")
    name  | age | rank
    ------------------
    James | 10  | 2
    Mark  | 7   | 3
    Lila  | 74  | 1
"""

import setpath
import re
from vtout import SourceNtoOne
from lib.dsv import writer
import gzip
from lib.ziputils import ZipIter
import functions
from lib.vtoutgtable import vtoutpugtformat
import lib.inoutparsing
registered=True



def fileit(p,append=False):
    if append:
        return open(p,"a")
    return open(p,"w")

def getoutput(p,append,compress,comptype):
    source=p
    it=None
    

    if compress and ( comptype=='zip'):
        it=ZipIter(source,"w")
    elif compress and ( comptype=='gzip' or comptype=='gz'):
            itt=fileit(source+'.gz')
            it=gzip.GzipFile(mode="w",fileobj=itt)
    else:
        it=fileit(source,append)
    return it


def outputData(diter,*args,**formatAgrs):
    dialect=lib.inoutparsing.defaultcsv()
    ### Parameter handling ###
    where=None
    if len(args)>0:
        where=args[0]
    elif 'file' in formatAgrs:
        where=formatAgrs['file']
    else:
        raise functions.OperatorError(__name__.rsplit('.')[-1],"No destination provided")
    if 'file' in formatAgrs:
        del formatAgrs['file']

    if 'mode' not in formatAgrs:
        formatAgrs['mode']='csv'
    if 'header' not in formatAgrs:
        header=False
    else:
        header=formatAgrs['header']
        del formatAgrs['header']

    if 'compression' not in formatAgrs:
       formatAgrs['compression']=False
    if 'compressiontype' not in formatAgrs:
        formatAgrs['compressiontype']='zip'

    if 'dialect' in formatAgrs:
        dialect=formatAgrs['dialect']
        del formatAgrs['dialect']
    append=False
    if 'append' in formatAgrs:
        append=formatAgrs['append']
        del formatAgrs['append']




    fileIter=getoutput(where,append,formatAgrs['compression'],formatAgrs['compressiontype'])

    del formatAgrs['compressiontype']
    del formatAgrs['compression']
    try:
        if formatAgrs['mode']=='csv':
            del formatAgrs['mode']
            csvprinter=writer(fileIter,dialect,**formatAgrs)
            for row,headers in diter:
                if header:
                    csvprinter.writerow([h[0] for h in headers])
                    header=False
                csvprinter.writerow(row)
        elif formatAgrs['mode']=='gtable':
            vtoutpugtformat(fileIter,diter,simplejson=False)
        elif formatAgrs['mode']=='gjson':

            vtoutpugtformat(fileIter,diter,simplejson=True)

        elif formatAgrs['mode']=='html':
            raise functions.OperatorError(__name__.rsplit('.')[-1],"HTML format not available yet")
        elif formatAgrs['mode']=='plain':
            for row,headers in diter:
                fileIter.write(((''.join(row))+'\n').encode('utf-8'))
        else:
            raise functions.OperatorError(__name__.rsplit('.')[-1],"Unknown mode value")

    except StopIteration,e:
        pass

    fileIter.close()


boolargs=lib.inoutparsing.boolargs+['append','header','compression']


def Source():
    global boolargs, nonstringargs
    return SourceNtoOne(outputData,boolargs, lib.inoutparsing.nonstringargs,lib.inoutparsing.needsescape)


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