# coding: utf-8

import setpath
import functions

def ifthenelse(*args):
    """
    .. function:: ifthenelse(condition, x, y)
    
        Returns *x* if *condition* is true, else returns *y*.

    .. templateforparams Parameters:
        :condition: exception type
        :x: exception value
        :y: traceback object
        :returns: true or false

    .. note::

        The difference with the *if* construct in most programming languages
        is that *x* and *y* expressions will always be evaluated.

    Examples:

    >>> sql("select ifthenelse(1>0,'yes','no') as answer")
    answer
    ------
    yes
    """
    if len(args)<2:
        raise functions.OperatorError("ifthenelse","operator needs at least two inputs")

    if args[0]:
        return args[1]
    else:
        if len(args)>2:
            #print "Length is:%s Returning val %s" %(len(args),args[2])
            return args[2]
        return None

ifthenelse.registered=True

def raiseif(*args):
    """
    .. function:: raiseif(condition [, messsage])
    
        If condition is true, raises an error. If message is provided, the message is included in
        raised error.

    Examples:

    >>> sql("select raiseif(1=1,'exception') as answer") #doctest:+ELLIPSIS +NORMALIZE_WHITESPACE
    Traceback (most recent call last):
    ...
    OperatorError: Madis SQLError:
    Operator RAISEIF: exception
    
    >>> sql("select raiseif(1=0,'exception') as answer") #doctest:+ELLIPSIS +NORMALIZE_WHITESPACE
    answer
    ------
    0

    >>> sql("select raiseif(1=1) as answer") #doctest:+ELLIPSIS +NORMALIZE_WHITESPACE
    Traceback (most recent call last):
    ...
    OperatorError: Madis SQLError:
    Operator RAISEIF: an error was found

    """

    if len(args)>3:
        raise functions.OperatorError('raiseif','operator needs one or two input')

    if args[0]:
        if len(args)==2:
            raise functions.OperatorError('raiseif', args[1])
        else:
            raise functions.OperatorError('raiseif', 'an error was found')

    return args[0]

raiseif.registered=True



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
