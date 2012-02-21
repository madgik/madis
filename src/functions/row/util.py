# coding: utf-8
import setpath
from gzip import zlib
import subprocess
import functions

def gz(*args):

    """
    .. function:: gz(text) -> gzip compressed blob

    Function *gz* compresses its input with gzip's maximum compression level.

    Examples:

    >>> table1('''
    ... "qwerqewrqwerqwerqwerqwerqwer"
    ... "asdfasdfasdfasdfasdfasdfsadf"
    ... ''')
    >>> sql("select length(a), length(gz(a)) from table1")
    length(a) | length(gz(a))
    -------------------------
    28        | 20
    28        | 18

    """

    return buffer(zlib.compress(args[0], 9))

gz.registered=True

def ungz(*args):

    """
    .. function:: ungz(blob) -> text

    Function *ungz* decompresses gzip blobs. If the input blobs aren't gzip
    compressed, then it just returns them as they are.

    Examples:

    >>> table1('''
    ... "qwerqwerqwer"
    ... "asdfasdfasdf"
    ... ''')
    >>> sql("select ungz(gz(a)) from table1")
    ungz(gz(a))
    ------------
    qwerqwerqwer
    asdfasdfasdf

    >>> sql("select ungz('string'), ungz(123)")
    ungz('string') | ungz(123)
    --------------------------
    string         | 123

    """

    try:
        return zlib.decompress(args[0])
    except:
        return args[0]

ungz.registered=True

def failif(*args):
    """
    .. function:: failif(condition [, messsage])

        If condition is true, raises an error. If message is provided, the message is included in
        raised error.

    Examples:

    >>> sql("select failif(1=1,'exception') as answer") #doctest:+ELLIPSIS +NORMALIZE_WHITESPACE
    Traceback (most recent call last):
    ...
    OperatorError: Madis SQLError:
    Operator FAILIF: exception

    >>> sql("select failif(1=0,'exception') as answer") #doctest:+ELLIPSIS +NORMALIZE_WHITESPACE
    answer
    ------
    0

    >>> sql("select failif(1=1) as answer") #doctest:+ELLIPSIS +NORMALIZE_WHITESPACE
    Traceback (most recent call last):
    ...
    OperatorError: Madis SQLError:
    Operator FAILIF: an error was found

    """

    if len(args)>3:
        raise functions.OperatorError('failif','operator needs one or two input')

    if args[0]:
        if len(args)==2:
            raise functions.OperatorError('failif', args[1])
        else:
            raise functions.OperatorError('failif', 'an error was found')

    return args[0]

failif.registered=True

def execprogram(*args):
    """
    .. function:: execprogram(stdin=None, program_name, parameters) -> text or blob

    Function *execprogram* executes a shell command and returns its output. If the
    value of the first parameter is not *null*, it will be provided in program's Standard Input.

    Examples:

    >>> table1('''
    ... echo    test
    ... echo    1
    ... ''')
    >>> sql("select execprogram(null, a, b) from table1")
    execprogram(null, a, b)
    -----------------------
    test
    1

    >>> sql("select execprogram('test', 'cat')")
    execprogram('test', 'cat')
    --------------------------
    test

    >>> sql('''select execprogram('test', 'cat', '-n')''') #doctest:+ELLIPSIS +NORMALIZE_WHITESPACE
    execprogram('test', 'cat', '-n')
    --------------------------------
         1        test

    >>> sql("select execprogram(null, 'NON_EXISTENT_PROGRAM')") #doctest:+ELLIPSIS +NORMALIZE_WHITESPACE
    Traceback (most recent call last):
    ...
    OperatorError: Madis SQLError:
    Operator EXECPROGRAM: OSError(2, 'No such file or directory')
    """

    if len(args)<2:
        raise functions.OperatorError('execprogram', "First parameter should be data to provide to program's STDIN, or null")

    outtext=errtext=''
    try:
        p=subprocess.Popen([unicode(x) for x in args[1:]], stdin=subprocess.PIPE if args[0]!=None else None, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if args[0]==None:
            outtext, errtext=p.communicate()
        else:
            if type(args[0]) not in (buffer, str, unicode):
                args[0]=unicode(args[0])
            outtext, errtext=p.communicate(args[0])
    except Exception,e:
        raise functions.OperatorError('execprogram', functions.mstr(e))

    if len(outtext)==0 and p.returncode!=0:
        raise functions.OperatorError('execprogram', functions.mstr(errtext))

    try:
        outtext=unicode(outtext, 'utf-8')
    except:
        return buffer(outtext)

    return outtext

execprogram.registered=True


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
