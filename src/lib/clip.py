#! /usr/bin/env python2.5

from __future__ import with_statement
from contextlib import contextmanager

try:
    import win32clipboard as wcb
    import win32con

    @contextmanager
    def WinClipboard():
        """
        A context manager for using the windows clipboard safely.
        """
        try:
            wcb.OpenClipboard()
            yield
        finally:
            wcb.CloseClipboard()

    def getcbtext():
        with WinClipboard():
            return wcb.GetClipboardData(win32con.CF_TEXT)

    def setcbtext(text):
        with WinClipboard():
            wcb.EmptyClipboard()
            wcb.SetClipboardText(text)

except ImportError, e:
    # try gtk.  If that doesn't work, just let the exception go
    import gtk

    def getcbtext():
        return gtk.Clipboard().wait_for_text()

    def setcbtext(text):
        cb = gtk.Clipboard()
        cb.set_text(text)
        cb.store()

def replaceclipboard(fn):
    """
    Modify text on the clipboard.

    fn: a callable object that maps strings to strings.

    >>> setcbtext("This is some text.")
    >>> replaceclipboard(lambda s : s.upper())
    >>> getcbtext()
    'THIS IS SOME TEXT.'
    """
    text = getcbtext()
    newtext = fn(text)
    setcbtext(newtext)

def _test():
    import doctest
    doctest.testmod()

if __name__ == '__main__':
    _test()
