import unittest
import hew
from unittest.mock import patch

class Test_Tokenizer(unittest.TestCase):
    def setUp(self):
        self.target = hew.normalizer.tokenize

    def test_happy(self):
        s = 'Happy Path!'
        expected = ['Happy', 'Path', '!']
        actual = list(self.target(s))
        self.assertEqual(expected, actual)

    def test_empty(self):
        s = ''
        expected = []
        actual = list(self.target(s))
        self.assertEqual(expected, actual)

    def test_other_whitepsace(self):
        s = 'This\tstring\nhas\rother\ttoken\rmarkers.'
        expected = ['This', '\t', 'string', '\n', 'has', '\r', 'other', '\t', 
                    'token', '\r', 'markers', '.']
        actual = list(self.target(s))
        self.assertEqual(expected, actual)

class Test_Normalizer(unittest.TestCase):
    def setUp(self):
        self.target = hew.Normalizer()
        # This is a test sentence. With punctuation, acronyms and accents!
        self.data = '\xde\xef\u015d is a TESTSENT. With punct, acro & a\u0109\u010bents!'

    # -------------------------------------------------------------------------

    def test_ascii_happy(self):
        expected = 'This is a TESTSENT. With punct, acro & accents!'
        actual = self.target.to_ascii(self.data)
        self.assertEqual(expected, actual)

    @patch('hew.normalizer.buildRomanizeReplace', wraps=hew.normalizer.buildRomanizeReplace)
    def test_ascii_list(self, map1):
        expected = 'This is a TESTSENT. With punct, acro & accents!'
        for i in range(4):
            with self.subTest(i=i):
                actual = self.target.to_ascii(self.data)
                self.assertEqual(expected, actual)
                self.assertEqual(1, map1.call_count)

    def test_ascii_extra_char_expands(self):
        self.target.charExpand = {'a': 'aa', 'i' : 'ii', 'e': 'ee', 'o' : 'oo'}
        expected = 'This iis aa TESTSENT. Wiith punct, aacroo & aacceents!'
        actual = self.target.to_ascii(self.data)
        self.assertEqual(expected, actual)

    def test_ascii_extra_token_expands(self):
        self.target.tokenExpand = {'TESTSENT' : ['test', 'sentence']}
        expected = 'This is a TESTSENT. With punct, acro & accents!'
        actual = self.target.to_ascii(self.data)
        self.assertEqual(expected, actual)

    def test_ascii_extra_char_replace(self):
        self.target.charReplace = {'t': 'x', 'T': 'X'}
        expected = 'Xhis is a XESXSENX. Wixh puncx, acro & accenxs!'
        actual = self.target.to_ascii(self.data)
        self.assertEqual(expected, actual)

    def test_ascii_extra_token_replace(self):
        self.target.tokenReplace.update({'punct':'punctuation', 'acro':'acronyms'})
        expected = 'This is a TESTSENT. With punct, acro & accents!'
        actual = self.target.to_ascii(self.data)
        self.assertEqual(expected, actual)

    def test_ascii_extra_char_ignore(self):
        self.target.charIgnore = ['i']
        expected = 'Ths s a TESTSENT. Wth punct, acro & accents!'
        actual = self.target.to_ascii(self.data)
        self.assertEqual(expected, actual)

    def test_ascii_extra_token_ignore(self):
        self.target.tokenIgnore.extend(['punct'])
        expected = 'This is a TESTSENT. With punct, acro & accents!'
        actual = self.target.to_ascii(self.data)
        self.assertEqual(expected, actual)

    # -------------------------------------------------------------------------

    def test_key_happy(self):
        expected = 'thisistestsentwithpunctacroandaccents'
        actual = self.target.to_key(self.data)
        self.assertEqual(expected, actual)

    @patch('hew.normalizer.buildRomanizeReplace', wraps=hew.normalizer.buildRomanizeReplace)
    def test_key_list(self, map1):
        expected = 'thisistestsentwithpunctacroandaccents'
        for i in range(4):
            with self.subTest(i=i):
                actual = self.target.to_key(self.data)
                self.assertEqual(expected, actual)
                self.assertEqual(1, map1.call_count)

    def test_key_extra_char_expand(self):
        self.target.charExpand = {'a': 'aa', 'i' : 'ii', 'e': 'ee', 'o' : 'oo'}
        expected = 'thisiisteestseentwiithpunctaacrooaandaacceents'
        actual = self.target.to_key(self.data)
        self.assertEqual(expected, actual)

    def test_key_extra_token_expand(self):
        self.target.tokenExpand = {'TESTSENT' : ['test', 'sentence']}
        expected = 'thisistestsentencewithpunctacroandaccents'
        actual = self.target.to_key(self.data)
        self.assertEqual(expected, actual)

    def test_key_extra_char_replace(self):
        self.target.charReplace = {'t': 'x'}
        expected = 'xhisisxesxsenxwixhpuncxacroandaccenxs'
        actual = self.target.to_key(self.data)
        self.assertEqual(expected, actual)

    def test_key_extra_token_replace(self):
        self.target.tokenReplace.update({'punct':'punctuation', 'acro':'acronyms'})
        expected = 'thisistestsentwithpunctuationacronymsandaccents'
        actual = self.target.to_key(self.data)
        self.assertEqual(expected, actual)

    def test_key_extra_char_ignore(self):
        self.target.charIgnore = ['i']
        expected = 'thsstestsentwthpunctacroandaccents'
        actual = self.target.to_key(self.data)
        self.assertEqual(expected, actual)

    def test_key_extra_token_ignore(self):
        self.target.tokenIgnore.extend(['punct'])
        expected = 'thisistestsentwithacroandaccents'
        actual = self.target.to_key(self.data)
        self.assertEqual(expected, actual)

    # -------------------------------------------------------------------------

    def test_windows_file_happy(self):
        data = '***Is <\xde\xef\u015d> a filename?'
        expected = 'Is _\xde\xef\u015d_ a filename'
        actual = self.target.for_windows_file(data)
        self.assertEqual(expected, actual)

    @patch('hew.normalizer.windowsFileNameReserved', wraps=hew.normalizer.windowsFileNameReserved)
    def test_windows_file_list(self, map):
        data = '***Is <\xde\xef\u015d> a filename?'
        expected = 'Is _\xde\xef\u015d_ a filename'
        for i in range(4):
            with self.subTest(i=i):
                actual = self.target.for_windows_file(data)
                self.assertEqual(expected, actual)
                self.assertEqual(1, map.call_count)

    # -------------------------------------------------------------------------

    def test_query_string_happy(self):
        expected = 'this+is+testsent.+with+punct%2C+acro+and+accents%21'
        actual = self.target.for_query_string(self.data)
        self.assertEqual(expected, actual)

    def test_query_string_encode(self):
        expected = '%21%25'
        actual = self.target.for_query_string('! %')
        self.assertEqual(expected, actual)

    @patch('hew.normalizer.buildRomanizeReplace', wraps=hew.normalizer.buildRomanizeReplace)
    def test_query_string_list(self, map1):
        expected = 'this+is+testsent.+with+punct%2C+acro+and+accents%21'
        for i in range(4):
            with self.subTest(i=i):
                actual = self.target.for_query_string(self.data)
                self.assertEqual(expected, actual)
                self.assertEqual(1, map1.call_count)

    def test_query_string_extra_char_expand(self):
        self.target.charExpand = {'a': 'aa', 'i' : 'ii', 'e': 'ee', 'o' : 'oo'}
        expected = 'this+iis+teestseent.+wiith+punct%2C+aacroo+aand+aacceents%21'
        actual = self.target.for_query_string(self.data)
        self.assertEqual(expected, actual)

    def test_query_string_extra_token_expand(self):
        self.target.tokenExpand = {'TESTSENT' : ['test', 'sentence']}
        expected = 'this+is+test+sentence.+with+punct%2C+acro+and+accents%21'
        actual = self.target.for_query_string(self.data)
        self.assertEqual(expected, actual)

    def test_query_string_extra_char_replace(self):
        self.target.charReplace = {'t': 'x'}
        expected = 'xhis+is+xesxsenx.+wixh+puncx%2C+acro+and+accenxs%21'
        actual = self.target.for_query_string(self.data)
        self.assertEqual(expected, actual)

    def test_query_string_extra_token_replace(self):
        self.target.tokenReplace.update({'punct':'punctuation', 'acro':'acronyms'})
        expected = 'this+is+testsent.+with+punctuation%2C+acronyms+and+accents%21'
        actual = self.target.for_query_string(self.data)
        self.assertEqual(expected, actual)

    def test_query_string_extra_char_ignore(self):
        self.target.charIgnore = ['i']
        expected = 'ths+s+testsent.+wth+punct%2C+acro+and+accents%21'
        actual = self.target.for_query_string(self.data)
        self.assertEqual(expected, actual)

    def test_query_string_extra_token_ignore(self):
        self.target.tokenIgnore.extend(['punct'])
        expected = 'this+is+testsent.+with%2C+acro+and+accents%21'
        actual = self.target.for_query_string(self.data)
        self.assertEqual(expected, actual)

if __name__ == '__main__':
    unittest.main()
