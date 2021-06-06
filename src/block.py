from hashlib import sha256

import time
import random
import math
import sys

class CmpEBlock():
    def __init__(self, index, transactions, prevBlockHash, proofOfWork=0, timestamp=time.time()):
        self.index = index
        self.timestamp = timestamp
        self.transactions = transactions
        self.prevBlockHash = prevBlockHash
        self.proofOfWork = proofOfWork
        self.currBlockHash = self.calculateCurrBlockHash()

    def validateBlock(self, difficulty):
        iter_count = 0
        calculatedHash = self.currBlockHash
        while not calculatedHash.startswith("0" * int(difficulty)):
            iter_count += 1
            self.proofOfWork = random.randint(0, sys.maxsize * 2 + 1)
            calculatedHash = self.calculateCurrBlockHash()
        
        print('iteration count:', iter_count)
        return self.proofOfWork, calculatedHash

    def hasValidTransactions(self):
        for transaction in self.transactions:
            try:
                if not transaction.isTransactionValid():
                    return False
            except:
                print('Failed to validate transaction.')
                return False
        
        return True
    
    def calculateCurrBlockHash(self):
        block = str(self.index) + str(self.timestamp) + str(self.transactions) + str(self.prevBlockHash) + str(self.proofOfWork)
        return sha256(block.encode()).hexdigest()
