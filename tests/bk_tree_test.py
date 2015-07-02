import os
import unittest
import hew

class Test_BKTree(unittest.TestCase):
    def setUp(self):
        fileName = os.path.join(os.path.dirname(__file__), 'english_common_1000.txt')
        with open(fileName, 'r') as f:
            self.words1000 = [line.strip() for line in f]

        self.target = hew.BKNode('pear')
        for w in self.words1000:
            self.target.insert(w);
        
    def test_searchFord(self):
        results = []
        probes = self.target.search('ford', 1, results)
        self.assertEqual(191, probes)
        self.assertEqual(4, len(results))
        self.assertIn('for', results)

    def test_searchPerson(self):
        results = []
        probes = self.target.search('person', 2, results)
        self.assertEqual(356, probes)
        self.assertEqual(5, len(results))
        self.assertIn('reason', results)

if __name__ == '__main__':
    unittest.main()
