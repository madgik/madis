import collections

class peekable(object):
    """ An iterator that supports a peek operation.  Example usage:
    >>> p = peekable(range(4))
    >>> p.peek( )
    0
    >>> p.next(1)
    [0]
    >>> p.peek(3)
    [1, 2, 3]
    >>> p.next(2)
    [1, 2]
    >>> p.peek(2)
    Traceback (most recent call last):
    ...
    StopIteration
    >>> p.peek(1)
    [3]
    >>> p.next(2)
    Traceback (most recent call last):
    ...
    StopIteration
    >>> p.next( )
    3
    """
    def __init__(self, iterable):
        self._iterable = iter(iterable)
        self._cache = collections.deque( )
    def __iter__(self):
        return self
    def _fillcache(self, n):
        if n is None:
            n = 1
        while len(self._cache) < n:
            self._cache.append(self._iterable.next( ))
    def next(self, n=None):
        self._fillcache(n)
        if n is None:
            result = self._cache.popleft( )
        else:
            result = [self._cache.popleft( ) for i in range(n)]
        return result
    def peek(self, n=None):
        self._fillcache(n)
        if n is None:            
            result = self._cache[0]
        else:
            result = [self._cache[i] for i in range(n)]
        return result
    def maxpeek(self, n=None):
        try:
            self._fillcache(n)
        except StopIteration:
            n=len(self._cache)
            pass
        if n is None:
            result = self._cache[0]
        else:
            result = [self._cache[i] for i in range(n)]
        return result

    def peekall(self):
        while True:
            try:
                self._cache.append(self._iterable.next( ))
            except StopIteration:                
                break
        return list(self._cache)



