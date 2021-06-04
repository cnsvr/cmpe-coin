from time import time
from src.block import Block
import unittest

class TestBlock(unittest.TestCase):
    def test_calculate_curr_block_hash(self):
        test_block = Block(0, time.time(), [], "00001234")
        self.assertIsInstance(test_block.calculateCurrBlockHash(), 'string', "Should be a string")
        self.assert
        self.assertGreater(len(test_block.calculateCurrBlockHash()), 0, "Should be initialized.")

test_block = Block(0, time.time(), [], "00001234")

assert(test_block.calculateCurrBlockHash(), )