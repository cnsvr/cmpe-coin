from block import CmpEBlock
import time
import unittest

class TestBlock(unittest.TestCase):
    def test_calculate_curr_block_hash(self):
        test_block = CmpEBlock(0, time.time(), [], "00001234")
        self.assertTrue(isinstance(test_block.calculateCurrBlockHash(), type("")), "Should be a string")
        self.assertGreater(len(test_block.calculateCurrBlockHash()), 0, "Should be initialized.")
    
    def test_validate_block(self):
        test_block = CmpEBlock(0, [], "00001234", timestamp=time.time())

        difficulty = 3
        
        pow, calc_hash = test_block.validateBlock(difficulty)
        self.assertGreater(len(calc_hash), 0, "Should be a string.")
        self.assertTrue(isinstance(pow, type(1)), "Should be an integer.")

        second_test_block = CmpEBlock(0, [], "00001234", timestamp=test_block.timestamp, proofOfWork=pow)
        second_pow, second_calc_hash = second_test_block.validateBlock(difficulty)

        self.assertEqual(calc_hash, second_calc_hash, "Should be the same hash value.")
        self.assertEqual(pow, second_pow, "Should be the same proof of work value.")


if __name__ == '__main__':
    unittest.main()