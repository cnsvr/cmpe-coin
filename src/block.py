from hashlib import sha256
import json
import time
import random
import math

class Block():
    def __init__(self, index, transactions, prevBlockHash, proofOfWork=0, timestamp=time.time()):
        self.index = index
        self.timestamp = timestamp
        self.transactions = transactions
        self.prevBlockHash = prevBlockHash
        self.proofOfWork = proofOfWork

    def validateBlock(self, difficulty):
        iter_count = 0
        calculatedHash = self.currBlockHash
        while not calculatedHash.startswith("0" * int(difficulty)):
            iter_count += 1
            self.proofOfWork = random.randint(0, math.inf)
            calculatedHash = self.calculateCurrBlockHash()
        pass

    def hasValidTransactions(self):
        for transaction in self.transactions:
            if not transaction.isTransactionValid():
                return False
        
        return True
    
    def calculateCurrBlockHash(self):
        block = str(self.index) + str(self.timestamp) + str(self.transactions) + str(self.prevBlockHash) + str(self.proofOfWork)
        self.currBlockHash = sha256(block).hexdigest()
        return self.currBlockHash
