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
    except KeyboardInterrupt:
        raise
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
    .. function:: execprogram(stdin=null, program_name, parameters, [raise_error]) -> text or blob

    Function *execprogram* executes a shell command and returns its output. If the
    value of the first argument is not *null*, the arguments value will be pushed in program's Standard Input.

    If the program doesn't return a *0* return code, then a madIS error will be raised, containing
    the contents of the program's error stream.

    If the last argument of *execprogram* is set to *null*, then all program errors will be returned as *null*
    (see "cat non_existent_file" examples below).

    Every one of the program's parameters must be provided as different arguments of the *execprogram* call
    (see "cat -n" example below).

    .. note::
        Function *execprogram* tries by default to convert the program's output to UTF-8. If the conversion
        isn't succesfull, then it returns the output as a binary blob.

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

    >>> sql("select execprogram(null, null, '-l')") #doctest:+ELLIPSIS +NORMALIZE_WHITESPACE
    Traceback (most recent call last):
    ...
    OperatorError: Madis SQLError:
    Operator EXECPROGRAM: Second parameter should be the name of the program to run

    >>> sql("select execprogram(null, null, '-l', null)") #doctest:+ELLIPSIS +NORMALIZE_WHITESPACE
    execprogram(null, null, '-l', null)
    -----------------------------------
    None

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

    >>> sql("select execprogram(null, 'cat', 'non_existent_file')") #doctest:+ELLIPSIS +NORMALIZE_WHITESPACE
    Traceback (most recent call last):
    ...
    OperatorError: Madis SQLError:
    Operator EXECPROGRAM: cat: non_existent_file: No such file or directory

    >>> sql("select execprogram(null, 'cat', 'non_existent_file', null)") #doctest:+ELLIPSIS +NORMALIZE_WHITESPACE
    execprogram(null, 'cat', 'non_existent_file', null)
    ---------------------------------------------------
    None
    """

    if len(args)<2:
        raise functions.OperatorError('execprogram', "First parameter should be data to provide to program's STDIN, or null")

    raise_error=False
    if len(args)>2 and args[-1]==None:
        raise_error=True

    if args[1]==None:
        if raise_error:
            return None
        else:
            raise functions.OperatorError('execprogram', "Second parameter should be the name of the program to run")

    outtext=errtext=''
    try:
        p=subprocess.Popen([unicode(x) for x in args[1:] if x!=None], stdin=subprocess.PIPE if args[0]!=None else None, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if args[0]==None:
            outtext, errtext=p.communicate()
        else:
            if type(args[0]) not in (buffer, str, unicode):
                args[0]=unicode(args[0])
            outtext, errtext=p.communicate(args[0])
    except Exception,e:
        raise functions.OperatorError('execprogram', functions.mstr(e))

    if p.returncode!=0:
        if raise_error:
            return None
        else:
            raise functions.OperatorError('execprogram', functions.mstr(errtext).strip())

    try:
        outtext=unicode(outtext, 'utf-8')
    except KeyboardInterrupt:
        raise
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
