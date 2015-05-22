import unittest
import hew.c45 as sut
import sys

class Test_C45_test(unittest.TestCase):
    def setUp(self):
        self.input = [{"arg1": "left", "arg2": "down", "arg3": "no", "result" : "yes", "argX" : "x" },
                      {"arg1": "left", "arg2": "up", "arg3": "yes", "result" : "no", "argX" : "x"  },
                      {"arg1": "right", "arg2": "down", "arg3": "yes", "result" : "yes", "argX" : "x"  },
                      {"arg1": "right", "arg2": "down", "arg3": "no", "result" : "no", "argX" : "x"  }]
        self.target = sut.C45.fromTable(self.input)

    def test_constructor_None(self):
        self.assertRaises(AssertionError, sut.C45, None)

    def test_constructor_NotDictionary(self):
        self.assertRaises(AssertionError, sut.C45, "Fail")

    def test_transpose(self):
        target = sut.C45.fromTable(self.input)
        assert(isinstance(target.columnSet, dict))
        assert(len(target.columnSet['result']) == 4)
        assert(len(target.columnSet['arg1']) == 4)
        assert(len(target.columnSet['arg2']) == 4)
        assert(len(target.columnSet['arg3']) == 4)
        self.assertEquals(sorted(set(target.columnSet['arg1'])), ['left', 'right'])

    def test_frequency(self):
        self.assertEquals(self.target.frequency('arg1', 'left'), 2)
        self.assertEquals(self.target.frequency('result', 'no'), 2)
        self.assertEquals(self.target.frequency('arg3', 'foo'), 0)

    def test_info(self):
        self.assertEquals(self.target.info('result'), 1)

    def test_infox(self):
        self.assertEquals(self.target.infox('arg1', 'result'), 1)

    def test_gain(self):
        self.assertEquals(self.target.gain('arg1', 'result'), 0)

    def test_uniques(self):
        self.assertEquals(sorted(self.target.uniques('result')), ['no', 'yes'])
        self.assertEquals(sorted(self.target.uniques('arg1')), ['left', 'right'])

    def test_isHomogeneous(self):
        self.assertTrue(self.target.isHomogeneous('argX'))
        self.assertFalse(self.target.isHomogeneous('arg1'))

    def test_get_indexes(self):
        self.assertEqual(self.target.get_indexes('arg3', 'no'), [0, 3])
        self.assertEqual(self.target.get_indexes('arg3', 'dunno'), [])
        self.assertEqual(self.target.get_indexes('arg2', 'down'),
                         [0, 2, 3])

    def test_get_values(self):
        self.assertEqual(self.target.get_values('arg1', [0, 2, 3]),
                         ['left', 'right', 'right'])
        self.assertEqual(self.target.get_values('arg3', [1, 3]),
                         ['yes', 'no'])
        self.assertEqual(self.target.get_values('arg1', []), [])
        self.assertEqual(self.target.get_values('arg1', [9, 12]), [])

    def test_buildPartition(self):
        expected = {
            'result': ['yes', 'no'],
            'arg1': ['left', 'right'],
            'arg2': ['down', 'down'],
            'arg3': ['no', 'no'],
            'argX': ['x', 'x']
        }
        self.assertEquals(self.target.buildPartition('arg3', 'no').columnSet, expected)
        expected = {
            'result': [],
            'arg1': [],
            'arg2': [],
            'arg3': [],
            'argX' : []
        }
        self.assertEquals(self.target.buildPartition('arg3', 'maybe').columnSet, expected)
        expected = {
            'result': ['yes', 'yes', 'no'],
            'arg1': ['left', 'right', 'right'],
            'arg2': ['down', 'down', 'down'],
            'arg3': ['no', 'yes', 'no'],
            'argX': ['x', 'x', 'x']
        }
        self.assertEquals(self.target.buildPartition('arg2', 'down').columnSet, expected)

    def test_partitionOnFeature(self):
        expected = [
        {   'result': ['yes', 'no'],
            'arg1': ['left', 'left'],
            'arg2': ['down', 'up'],
            'arg3': ['no', 'yes'],
            'argX': ['x', 'x']
        },
        {   'result': ['yes', 'no'],
            'arg1': ['right', 'right'],
            'arg2': ['down', 'down'],
            'arg3': ['yes', 'no'],
            'argX': ['x', 'x']
        }]
        actual = self.target.partitionOnFeature('arg1')
        leftIdx = 0 if actual[0].partitionValue == 'left' else 1
        rightIdx = 1 - leftIdx
        self.assertEquals(actual[leftIdx].columnSet, expected[0])
        self.assertEquals(actual[rightIdx].columnSet, expected[1])

    def test_makeDecisionTree(self):
        sut.C45.makeDecisionTree(self.input, 'result', sys.stdout)

if __name__ == '__main__':
    unittest.main()
