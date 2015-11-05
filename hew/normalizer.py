''' Provides a set of normalizing functions
'''
import re
import sys
import unicodedata
import itertools
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
    table = dict.fromkeys(c for c in range(sys.maxunicode)
                            if unicodedata.combining(_char(c)))

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
    table['\xc5'] = 'Aa'  # ring a
    table['\xc6'] = 'Ae'  # ligature
    table['\xde'] = 'Th'  # thorn
    table['\xdf'] = 'ss'  # sharp s
    table['\xe5'] = 'aa'  # ring a
    table['\xe6'] = 'ae'  # ligature
    table['\xfe'] = 'th'  # thorn
    return table

def buildPunctuationReplace():
    table = {0xa6 : '|',
             0xb4 : '\'',
             0xb6 : '*',
             0xd7 : 'x',

            0x2022 : '*',   # bullet
            0x2023 : '*',   
            0x2024 : '.',   
            0x2027 : '*',
            0x2032 : "'",
            0x2035 : "'",
            0x2039 : '<',
            0x203a : '>',
            0x2043 : '-',
            0x2044 : '/',
            0x204e : '*',
            0x2053 : '~',
            0x205f : ' ',
            }
    table.update({c :' ' for c in range(0x2000, 0x200a)})
    table.update({c :'-' for c in range(0x2010, 0x2015)})
    table.update({c :"'" for c in range(0x2018, 0x201b)})
    table.update({c :'"' for c in range(0x201c, 0x201f)})

    return table

def buildPunctuationExpand():
    return {'\xa9' : '(C)',
            '\xab' : '<<',
            '\xbb' : '>>',
            '\xae' : '(R)',
            '\xbc' : '1/4',
            '\xbd' : '1/2',
            '\xbe' : '3/4',
            '\x2025' : '..',
            '\x2026' : '...',
            '\x2033' : "''",
            '\x2034' : "'''",
            '\x2036' : "''",
            '\x2037' : "'''",
            '\x203c' : "!!",
            '\x2047' : "??",
            '\x2048' : "?!",
            '\x2049' : "!?",
            '\x2057' : "''''",
            }

def listAllPunctuation():
    """ Creates the list of all punctuation and symbols"""
    punctCat = ['P', 'S', 'Z']
    punct = [c
             for c in range(sys.maxunicode) 
             if unicodedata.category(_char(c))[0] in punctCat]
    return punct

def windowsFileNameReserved():
    reserved = ['\\', '/', ':', '*', '?', '"', '<', '>', '|', '.']
    return {ord(c):'_' for c in reserved}

def uriReserved():
    reserved =  ['!', '#', '$', '&', "'", '(', ')', '*', '+', ',', '/', ':', 
                 ';', '=', '?', '@', '[', ']', '%']
    return {c:'%{0:02X}'.format(ord(c)) for c in reserved}

#------------------------------------------------------------------------------
# Generators
#------------------------------------------------------------------------------

def tokenize(s):
    for i, x in enumerate(re.split('(\W+)', s)):
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
        self.tokenReplace = {'&': 'and', '+': 'and'}
        self.tokenIgnore = ['the', 'a', 'an']
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
