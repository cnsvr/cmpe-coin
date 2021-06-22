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


    def createInitialDummyBlock(self, addresses):
        transactions = []
        for address in addresses:
            initialTransaction = CmpETransaction(None, address, INITIAL_AMOUNT)
            transactions.append(initialTransaction)
        genesisBlock = Block(0, transactions, None)
        return genesisBlock
      

    def isChainValid(self, returnWallet = False):

        if len(self.chain) == 0:
            logging.info("Chain is empty, must have genesis block.")
            if returnWallet:
                return False, dict()
            return False

        walletDict = dict()

        # Check initial block of the chain. Must be the genesis block.
        if self.chain[0].prevBlockHash != None:
            logging.info("Genesis block has no previous block.")
            return False
        for transaction in self.chain[0].transactions:
            if transaction.amount != INITIAL_AMOUNT or transaction.fromAddress != None:
                walletDict[transaction.toAddress] = walletDict.get(transaction.toAddress, 0) + INITIAL_AMOUNT
                logging.info("Genesis block cannot have transactions with different amount and address.")
                if returnWallet:
                    return False, dict()
                return False

        index = 1

        while index < len(self.chain):
            lastBlock = self.chain[index]

            lastBlockHash = lastBlock.calculateCurrBlockHash()

            if not lastBlock.hasValidTransactions():
                logging.info("Chain has nonvalid transactions.")
                if returnWallet:
                    return False, dict()
                return False
            if not lastBlockHash.startswith("0" * int(self.difficulty)):
                logging.info("Block is not validated.")
                if returnWallet:
                    return False, dict()
                return False

            prevBlock = self.chain[index - 1]

            if lastBlock.prevBlockHash != prevBlock.calculateCurrBlockHash():
                logging.info("Chain is not properly linked.")
                if returnWallet:
                    return False, dict()
                return False


            for transaction in lastBlock.transactions:
                currentWallet = walletDict.get(transaction.fromAddress, 0)
                if transaction.amount > currentWallet:
                    logging.info(f"{transaction.fromAddress} spent more than it has. Chain not valid.")
                    if returnWallet:
                        return False, dict()
                    return False
                walletDict[transaction.fromAddress] = walletDict.get(transaction.fromAddress, 0) - transaction.amount

            for transaction in lastBlock.transactions:
                walletDict[transaction.toAddress] = walletDict.get(transaction.toAddress, 0) + transaction.amount

            index = index + 1

        if returnWallet:
            return True, walletDict
        return True
 
    
    def addTransactionToPendingList(self, transx):
        if transx.isTransactionValid():
            self.pendingTransactions.append(transx)
            return True
        return False

    def validatePendingTransactions(self, rewardAddress):
        # TODO:
        # Mutex?
        # If new transactions are received during validation, should validation stop? 
        # New transactions while validating can be added to a new list.
        transactions = self.pendingTransactions.copy()
        transactions.append(CmpETransaction(None, rewardAddress, self.validationReward))
        newBlock = Block(0, transactions, self.chain[len(self.chain) - 1].calculateCurrBlockHash)
        newBlock.validateBlock(self.difficulty)
        return newBlock

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
