"""WebUtils.Funcs

This module provides some basic functions that are useful
in HTML and web development.

You can safely import * from WebUtils.Funcs if you like.

TO DO

* Document the 'codes' arg of htmlEncode/Decode.

"""


htmlForNone = '-'  # used by htmlEncode.

htmlCodes = [
	['&', '&amp;'],
	['<', '&lt;'],
	['>', '&gt;'],
	['"', '&quot;'],
	# ['\n', '<br>'],
]

htmlCodesReversed = htmlCodes[:]
htmlCodesReversed.reverse()

def htmlEncode(what, codes=htmlCodes):
	if what is None:
		return htmlForNone
	if hasattr(what, 'html'):
		# allow objects to specify their own translation to html
		# via a method, property or attribute
		ht = what.html
		if callable(ht):
			ht = ht()
		return ht
	what = str(what)
	return htmlEncodeStr(what, codes)

def htmlEncodeStr(s, codes=htmlCodes):
	"""Return the HTML encoded version of the given string.

	This is useful to display a plain ASCII text string on a web page.

	"""
	for code in codes:
		s = s.replace(code[0], code[1])
	return s

def htmlDecode(s, codes=htmlCodesReversed):
	"""Return the ASCII decoded version of the given HTML string.

	This does NOT remove normal HTML tags like <p>.
	It is the inverse of htmlEncode().

	"""
	for code in codes:
		s = s.replace(code[1], code[0])
	return s

_urlEncode = {}
for i in range(256):
	c = chr(i)
	_urlEncode[c] = c == ' ' and '+' \
		or i < 128 and (c.isalnum() or c in '_.-/') and c \
		or '%%%02X' % i

def urlEncode(s):
	"""Return the encoded version of the given string.

	The resulting string is safe for using as a URL.

	Identical to urllib.quote_plus(s) in Python 2.4,
	but faster for older Python versions.

	"""
	return ''.join(map(_urlEncode.get, s))

_urlDecode = {}
for i in range(256):
	_urlDecode['%02x' % i] = _urlDecode['%02X' % i] = chr(i)

try:
	UnicodeDecodeError
except NameError: # Python < 2.3
	class UnicodeDecodeError(Exception):
		pass

def urlDecode(s):
	"""Return the decoded version of the given string.

	Note that invalid URLs will not throw exceptions.
	For example, incorrect % codings will be ignored.

	Identical to urllib.unquote_plus(s) in Python 2.4,
	but faster and more exact for older Python versions.

	"""
	s = s.replace('+', ' ').split('%')
	for i in xrange(1, len(s)):
		t = s[i]
		try:
			s[i] = _urlDecode[t[:2]] + t[2:]
		except KeyError:
			s[i] = '%' + t
		except UnicodeDecodeError:
			s[i] = unichr(int(t[:2], 16)) + t[2:]
	return ''.join(s)

def htmlForDict(dict, addSpace=None, filterValueCallBack=None,
		maxValueLength=None, topHeading=None, isEncoded=None):
	"""Return an HTML string with a table where each row is a key-value pair."""
	if not dict:
		return ''
	keys = dict.keys()
	keys.sort()
	# A really great (er, bad) example of hardcoding.  :-)
	html = ['<table class="NiceTable">\n']
	if topHeading:
		html.append('<tr class="TopHeading"><th')
		html.append((type(topHeading) is type(())
			and '>%s</th><th>%s' or ' colspan="2">%s') % topHeading)
		html.append('</th></tr>\n')
	for key in keys:
		value = dict[key]
		if addSpace and addSpace.has_key(key):
			target = addSpace[key]
			value = (target + ' ').join(value.split(target))
		if filterValueCallBack:
			value = filterValueCallBack(value, key, dict)
		if maxValueLength and not isEncoded:
			value = str(value)
			if len(value) > maxValueLength:
				value = value[:maxValueLength] + '...'
		key = htmlEncode(key)
		if not isEncoded:
			value = htmlEncode(value)
		html.append('<tr><th align="left">%s</th><td>%s</td></tr>\n'
			% (key, value))
	html.append('</table>')
	return ''.join(html)

def requestURI(env):
	"""Return the request URI for a given CGI-style dictionary.

	Uses REQUEST_URI if available, otherwise constructs and returns it
	from SCRIPT_URL, SCRIPT_NAME, PATH_INFO and QUERY_STRING.

	"""
	uri = env.get('REQUEST_URI', None)
	if uri is None:
		uri = env.get('SCRIPT_URL', None)
		if uri is None:
			uri = env.get('SCRIPT_NAME', '') + env.get('PATH_INFO', '')
		query = env.get('QUERY_STRING', '')
		if query != '':
			uri += '?' + query
	return uri

def normURL(path):
	"""Normalizes a URL path, like os.path.normpath.

	Acts on a URL independant of operating system environment.

	"""
	if not path:
		return
	initialslash = path[0] == '/'
	lastslash = path[-1] == '/'
	comps = path.split('/')
	newcomps = []
	for comp in comps:
		if comp in ('', '.'):
			continue
		if comp != '..':
			newcomps.append(comp)
		elif newcomps:
			newcomps.pop()
	path = '/'.join(newcomps)
	if path and lastslash:
		path += '/'
	if initialslash:
		path = '/' + path
	return path
