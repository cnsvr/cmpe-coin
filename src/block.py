from hashlib import sha256

import time
import random
import math
import sys
import json

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
        
        print('iteration count:', iter_count,'block Hash: ',calculatedHash)
        self.currBlockHash = calculatedHash
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

    def convertTransactionsToJSON(self):
        json_transactions = []

        for transaction in self.transactions:
            json_transactions.append(transaction.toJSON())

        return json_transactions

    def __repr__(self):
        return self.toJSON()
        
    def toJSON(self):
        json_block = {}
        json_block['index'] = self.index
        json_block['timestamp'] = self.timestamp
        json_block['transactions'] = self.convertTransactionsToJSON()
        json_block['prevBlockHash'] = self.prevBlockHash if self.prevBlockHash else None
        json_block['proofOfWork'] = self.proofOfWork
        json_block['currBlockHash'] = self.currBlockHash
        return json.dumps(json_block, default=lambda o: o.__dict__, indent=4)
