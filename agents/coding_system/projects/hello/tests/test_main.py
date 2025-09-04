import unittest
import sys
sys.path.append('../')
from main import *

class TestMain(unittest.TestCase):
    def test_basic(self):
        self.assertTrue(True)

if __name__ == '__main__':
    unittest.main()