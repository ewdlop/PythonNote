import unittest
import sys

def process_integer(n):
    """ Example function that squares the input integer if it's valid. """
    if not isinstance(n, int):
        raise ValueError("Input must be an integer")
    return n * n

class TestIntegerExhaustion(unittest.TestCase):
    
    def test_integer_exhaustion(self):
        """ Tests integer input using exhaustion for large ranges. """
        min_test_value = -sys.maxsize - 1  # Equivalent to int.min in many cases
        max_test_value = sys.maxsize       # Equivalent to int.max
        
        # Test extreme values
        self.assertEqual(process_integer(min_test_value), min_test_value ** 2)
        self.assertEqual(process_integer(max_test_value), max_test_value ** 2)

        # Test smaller sample range to avoid excessive runtime
        for i in range(-1000, 1001):
            with self.subTest(i=i):
                self.assertEqual(process_integer(i), i * i)
        
        # Test common edge cases
        self.assertEqual(process_integer(0), 0)
        self.assertEqual(process_integer(1), 1)
        self.assertEqual(process_integer(-1), 1)
        
        # Test non-integer inputs
        with self.assertRaises(ValueError):
            process_integer("string")

        with self.assertRaises(ValueError):
            process_integer(5.5)

        with self.assertRaises(ValueError):
            process_integer(None)

if __name__ == '__main__':
    unittest.main()
