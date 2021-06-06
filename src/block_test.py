from hashlib import sha256
from block import CmpEBlock
import time
import unittest

class TestBlock(unittest.TestCase):
    def test_initialize_block(self):
        index = 0
        timestamp = time.time()
        transactions = [1,2,3,4]
        proofOfWork = 10
        prevBlockHash = "1234567890"

        test_block = CmpEBlock(index, transactions, prevBlockHash, proofOfWork=proofOfWork, timestamp=timestamp)

        self.assertEqual(test_block.index, index)
        self.assertEqual(test_block.timestamp, timestamp)
        self.assertEqual(test_block.transactions, transactions)
        self.assertEqual(test_block.prevBlockHash, prevBlockHash)
        self.assertEqual(test_block.proofOfWork, proofOfWork)

    def test_calculate_curr_block_hash(self):
        index = 0
        timestamp = time.time()
        transactions = [1,2,3,4]
        proofOfWork = 10
        prevBlockHash = "1234567890"

        test_block = CmpEBlock(index, transactions, prevBlockHash, proofOfWork=proofOfWork, timestamp=timestamp)
        self.assertTrue(isinstance(test_block.currBlockHash, type("")), "Should be a string")
        self.assertGreater(len(test_block.currBlockHash, 0, "Should be initialized."))

        block = str(test_block.index) + str(test_block.timestamp) + str(test_block.transactions) + str(test_block.prevBlockHash) + str(test_block.proofOfWork)
        h = sha256(block.encode()).hexdigest()

        self.assertEqual(test_block.currBlockHash, h, "Should be equal to the hash calculated.")
    
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

    def test_has_valid_transactions(self):
        index = 0
        timestamp = time.time()
        transactions = [1,2,3,4]
        proofOfWork = 10
        prevBlockHash = "1234567890"

        test_block = CmpEBlock(index, transactions, prevBlockHash, proofOfWork=proofOfWork, timestamp=timestamp)

        self.assertFalse(test_block.hasValidTransactions(), "Should fail validating invalid transaction array.")
        
        # TODO(eridincu): Add the test to check the functionality when the transactions are valid.

if __name__ == '__main__':
    unittest.main()