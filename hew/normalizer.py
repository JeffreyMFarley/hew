''' Provides a set of normalizing functions
'''
import os
import re
import sys
import unicodedata
import itertools
import csv
from pymonad.Reader import *
from pymonad.List import *
from pymonad.Maybe import * 

if sys.version >= '3':
    _char = chr
else:
    _char = unichr

#------------------------------------------------------------------------------
# builders
#------------------------------------------------------------------------------

def buildRomanizeReplace():
    ''' This table for the `translate` function replaces one character for another 
    '''
    table = {}
    for row in acquireUnicode():
        if row['General_Category'] == 'Mn':
            table[int(row['CodePoint'], 16)] = None
        
    # latin extended not handled by decombining
    table[0xd0] = ord('D')      # D bar
    table[0xf0] = ord('d')      # eth
    table[0xd8] = ord('O')      # oe
    table[0xf8] = ord('o')      # oe

    table[0x0110] = ord('D')    # D bar
    table[0x0111] = ord('d')    # d bar

    # polish
    table[0x0141] = ord('L')    # l with stroke
    table[0x0142] = ord('l')    # l with stroke

    # greek
    table[0x3b1] = ord('a')
    table[0x3b4] = ord('d')

    table[0xfeff] = ord(' ')
    return table

def buildRomanizeExpand():
    table = {}
    table[u'\xc5'] = u'Aa'  # ring a
    table[u'\xc6'] = u'Ae'  # ligature
    table[u'\xde'] = u'Th'  # thorn
    table[u'\xdf'] = u'ss'  # sharp s
    table[u'\xe5'] = u'aa'  # ring a
    table[u'\xe6'] = u'ae'  # ligature
    table[u'\xfe'] = u'th'  # thorn
    return table

def buildPunctuationReplace():
    table = {0xa6 : u'|',
             0xb4 : u'\'',
             0xb6 : u'*',
             0xd7 : u'x',

            0x2022 : u'*',   # bullet
            0x2023 : u'*',   
            0x2024 : u'.',   
            0x2027 : u'*',
            0x2032 : u"'",
            0x2035 : u"'",
            0x2039 : u'<',
            0x203a : u'>',
            0x2043 : u'-',
            0x2044 : u'/',
            0x204e : u'*',
            0x2053 : u'~',
            0x205f : u' ',
            }
    table.update({c :u' ' for c in range(0x2000, 0x200a)})
    table.update({c :u'-' for c in range(0x2010, 0x2015)})
    table.update({c :u"'" for c in range(0x2018, 0x201b)})
    table.update({c :u'"' for c in range(0x201c, 0x201f)})

    return table

def buildPunctuationExpand():
    return {u'\xa9' : u'(C)',
            u'\xab' : u'<<',
            u'\xbb' : u'>>',
            u'\xae' : u'(R)',
            u'\xbc' : u'1/4',
            u'\xbd' : u'1/2',
            u'\xbe' : u'3/4',
            u'\u2025' : u'..',
            u'\u2026' : u'...',
            u'\u2033' : u"''",
            u'\u2034' : u"'''",
            u'\u2036' : u"''",
            u'\u2037' : u"'''",
            u'\u203c' : u"!!",
            u'\u2047' : u"??",
            u'\u2048' : u"?!",
            u'\u2049' : u"!?",
            u'\u2057' : u"''''",
            }

def listAllPunctuation():
    """ Creates the list of all punctuation and symbols"""
    punctCat = ['P', 'S', 'Z']

    punct = []
    for row in acquireUnicode():
        if row['General_Category'][0] in punctCat:
            punct.append(int(row['CodePoint'], 16))
   
    return punct

def windowsFileNameReserved():
    reserved = ['\\', '/', ':', '*', '?', '"', '<', '>', '|', '.']
    return {ord(c):u'_' for c in reserved}

def uriReserved():
    reserved =  ['!', '#', '$', '&', "'", '(', ')', '*', '+', ',', '/', ':', 
                 ';', '=', '?', '@', '[', ']', '%']
    return {c:'%{0:02X}'.format(ord(c)) for c in reserved}

#------------------------------------------------------------------------------
# Generators
#------------------------------------------------------------------------------

def acquireUnicode():
    dirName = os.path.dirname(__file__)
    fileName = os.path.join(dirName, 'UnicodeData.txt')
    with open(fileName) as f:
        reader = csv.DictReader(f, delimiter=';')
        for row in reader:
            yield row

def tokenize(s):
    for i, x in enumerate(re.split('(\W+)', s, flags=re.UNICODE)):
        if i % 2 == 0:
            if x:
                yield x
        else:
            for c in x:
                if c != ' ':
                    yield c

def expandToken(table, tokens):
    for s in tokens:
        if s in table:
            for x in table[s]:
                yield x
        else:
            yield s

def window(seq, n=2):
    "Returns a sliding window (of width n) over data from the iterable"
    "   s -> (s0,s1,...s[n-1]), (s1,s2,...,sn), ...                   "
    " http://stackoverflow.com/questions/6822725/rolling-or-sliding-window-iterator-in-python "
    it = iter(seq)
    result = tuple(itertools.islice(it, n))
    if len(result) == n:
        yield result    
    for elem in it:
        result = result[1:] + (elem,)
        yield result

#------------------------------------------------------------------------------
# Monads
#------------------------------------------------------------------------------

@curry
def ignoreToken(table, s):
    return Nothing if s in table else Just(s)

@curry
def replaceToken(table, s):
    return Just(table[s]) if s in table else Just(s)

@curry
def replaceCharacters(table, s):
    b = unicodedata.normalize('NFKD', s)
    s = b.translate(table)
    return Just(s)

@curry
def expandCharacters(table, s):
    expanded = [table[c] if c in table else c for c in s]
    return Just(''.join(expanded))

#------------------------------------------------------------------------------
# Class
#------------------------------------------------------------------------------

class Normalizer(object):
    def __init__(self):
        self.tokenReplace = {u'&': u'and', u'+': u'and'}
        self.tokenIgnore = [u'the', u'a', u'an']
        self.tokenExpand = {}
        self.charExpand = {}
        self.charReplace = {}
        self.charIgnore = []

    #--------------------------------------------------------------------------
    # To ASCII
    #--------------------------------------------------------------------------

    def _build_asciifier(self):
        cr = buildRomanizeReplace()
        cr.update(buildPunctuationReplace())
        cr.update({ord(c):v for c,v in self.charReplace.items()})

        ce = buildRomanizeExpand()
        ce.update(buildPunctuationExpand())
        ce.update(self.charExpand)

        ci = {c:None for c in listAllPunctuation() if c > 0x7f}
        ci.update({ord(c):None for c in self.charIgnore})

        def curried(s):
            part = Just(s) 
            part >>= expandCharacters(ce)
            part >>= replaceCharacters(cr)
            part >>= replaceCharacters(ci)
        
            return part.value
        return curried

    @property
    def asciifier(self):
        try:
            return self._asciifier
        except AttributeError:
            self._asciifier = self._build_asciifier()
            return self._asciifier

    def to_ascii(self, s):
        return self.asciifier(s)

    #--------------------------------------------------------------------------
    # To Key
    #--------------------------------------------------------------------------

    def _build_keyer(self):
        cr = buildRomanizeReplace()
        cr.update({ord(c):v for c,v in self.charReplace.items()})

        ce = buildRomanizeExpand()
        ce.update(self.charExpand)

        ci = {c:None for c in listAllPunctuation()}
        ci.update({ord(c):None for c in self.charIgnore})

        def curried(s):
            parts = []
            for token in expandToken(self.tokenExpand, tokenize(s)):
                part = Just(token.lower()) 
                part >>= replaceToken(self.tokenReplace)
                part >>= ignoreToken(self.tokenIgnore)
                part >>= expandCharacters(ce)
                part >>= replaceCharacters(cr)
                part >>= replaceCharacters(ci)
                parts.append(part)

            joined = ''. join([x.value for x in parts if x.value])
            return joined
        return curried

    @property
    def keyer(self):
        try:
            return self._keyer
        except AttributeError:
            self._keyer = self._build_keyer()
            return self._keyer

    def to_key(self, s):
        return self.keyer(s)

    #--------------------------------------------------------------------------
    # Windows File Name
    #--------------------------------------------------------------------------

    def _build_windows_namer(self):
        r = windowsFileNameReserved()

        def curried(s):
            return s.translate(r).strip('_')
            
        return curried

    @property
    def windows_namer(self):
        try:
            return self._windows_namer
        except AttributeError:
            self._windows_namer = self._build_windows_namer()
            return self._windows_namer

    def for_windows_file(self, s):
        return self.windows_namer(s)

    #--------------------------------------------------------------------------
    # Query String
    #--------------------------------------------------------------------------

    def _build_queryfier(self):
        cr = buildRomanizeReplace()
        cr.update({ord(c):v for c,v in self.charReplace.items()})

        ce = buildRomanizeExpand()
        ce.update(self.charExpand)

        ci = {c:None for c in listAllPunctuation() if c > 0x7f}
        ci.update({ord(c):None for c in self.charIgnore})

        r = uriReserved()

        def curried(s):
            parts = []
            for token in expandToken(self.tokenExpand, tokenize(s)):
                part = Just(token.lower()) 
                part >>= replaceToken(self.tokenReplace)
                part >>= ignoreToken(self.tokenIgnore)
                part >>= expandCharacters(ce)
                part >>= replaceCharacters(cr)
                part >>= replaceCharacters(ci)
                part >>= expandCharacters(r)
                parts.append(part)

            delimited = []
            for pair in window([x.value for x in parts if x.value]):
                delimited.append(pair[0])
                if pair[1][0] not in ['.', '%']:
                    delimited.append('+')
            delimited.append(parts[-1].value)

            return ''.join(delimited)
        return curried

    @property
    def queryfier(self):
        try:
            return self._queryfier
        except AttributeError:
            self._queryfier = self._build_queryfier()
            return self._queryfier

    def for_query_string(self, s):
        return self.queryfier(s)

#------------------------------------------------------------------------------
# Main
#------------------------------------------------------------------------------

if __name__ == '__main__':
    pass    
        
