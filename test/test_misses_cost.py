import unittest

from metrics.misses_cost import misses_cost


class MyTestCase(unittest.TestCase):
    def test_something(self):
        self.assertEqual(misses_cost(), True)


if __name__ == '__main__':
    unittest.main()
