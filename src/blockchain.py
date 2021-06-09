import logging
from block import Block
from transaction import CmpETransaction

INITIAL_AMOUNT = 50

class CmpEBlockchain:
    def __init__(self, chain, pendingTransactions=[], validationReward=1, difficulty=20):
        self.chain = chain
        self.pendingTransactions = pendingTransactions
        self.validationReward = validationReward
        self.difficulty = difficulty


    def createInitialDummyBlock(self, address):
        initialTransaction = CmpETransaction(None, address, INITIAL_AMOUNT)
        genesisBlock = Block(0, [initialTransaction], None)
        return genesisBlock        

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
                logging.info("Chain has nonvalid transactions.")
                return False
            if not prevBlock.calculateCurrBlockHash().startswith("0" * int(self.difficulty)):
                logging.info("Block is not validated.")
                return False

            prevBlockHash = prevBlock.calculateCurrBlockHash()

            if prevBlockHash != lastBlock.prevBlockHash:
                logging.info("Chain is not properly linked.")
                return False

            lastBlock = prevBlock
        
        if len(self.chain[0].transactions) == 1 and self.chain[0].transactions[0].amount == INITIAL_AMOUNT and self.chain[0].fromAddress == None:
            return True

        logging.info("Genesis block is not correct.")
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
