import unittest

def sample_function(x):
    return x * 2

class TestFunctions(unittest.TestCase):

    def test_sample_function(self):
        self.assertEqual(sample_function(3), 6)
        self.assertEqual(sample_function(-1), -2)

if __name__ == '__main__':
    unittest.main()
