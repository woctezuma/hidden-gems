import unittest

import create_dict_using_json
import compute_stats

class TestCreateDictUsingJsonMethods(unittest.TestCase):

    def test_main(self):
        self.assertTrue(create_dict_using_json.main())

class TestComputeStatsMethods(unittest.TestCase):

    def test_main(self):
        self.assertTrue(compute_stats.main())

if __name__ == '__main__':
    unittest.main()

