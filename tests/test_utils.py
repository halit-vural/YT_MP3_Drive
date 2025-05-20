# Tests for utils.py *_*
import unittest
from src.utils import greet

class TestUtils(unittest.TestCase):
    def test_greet(self):
        """Test greet function returns correct message *_*"""
        self.assertEqual(greet(), "Welcome to YT MP3 Drive! *_*")

if __name__ == "__main__":
    unittest.main()
