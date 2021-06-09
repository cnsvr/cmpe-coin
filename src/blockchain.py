import logging
from block import Block

class CmpEBlockchain:
    def __init__(self, chain, pendingTransactions=[], validationReward=1, difficulty=20):
        self.chain = chain
        self.pendingTransactions = pendingTransactions
        self.validationReward = validationReward
        self.difficulty = difficulty

    def createInitialDummyBlock():
        pass

    def isChainValid(self):
        if len(self.chain) == 0:
            logging.info("Chain is empty, must have genesis block.")
            return False

        lastBlock = self.chain[-1]
        if not lastBlock.hasValidTransactions():
            return False
        if not lastBlock.calculateCurrBlockHash().startswith("0" * int(self.difficulty)):
            return False

        index = len(self.chain)-2

        while index > 0:
            prevBlock = self.chain[index]

            if not prevBlock.hasValidTransactions():
                return False
            if not prevBlock.calculateCurrBlockHash().startswith("0" * int(self.difficulty)):
                return False

            prevBlockHash = prevBlock.calculateCurrBlockHash()

            if prevBlockHash != lastBlock.prevBlockHash:
                logging.info("Chain is not properly linked.")
                return False

            lastBlock = prevBlock

        if len(self.chain[0].transactions) == 0 and self.chain[0].prevBlockHash == None:
            logging.info("Genesis block is not correct.")
            return True
        
        return False
    
    def addTransactionToPendingList(transx):
        self.pendingTransactions.append(transx)
    
    def validatePendingTransactions(rewardAddress):
        pass

    def getBalanceOf(self, address):
        balance = 0

        for transaction in self.getAllTransactionsFor(address):
            if transaction.fromAddress == address:
                balance -= transaction.amount
            else:
                balance += transaction.amount

        return balance

    def getAllTransactionsFor(self, address):
        transactions = []

        for block in self.chain:
            for transaction in block.transactions:
                if transaction.fromAddress == address or transaction.toAddress == address:
                    transactions.append(transaction)

        return transactions
