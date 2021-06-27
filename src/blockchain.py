import logging
from block import CmpEBlock
from transaction import CmpETransaction

INITIAL_AMOUNT = 50

class CmpEBlockchain:
    def __init__(self, chain, pendingTransactions=[], validationReward=1, difficulty=2):
        self.chain = chain
        self.pendingTransactions = pendingTransactions
        self.validationReward = validationReward
        self.difficulty = difficulty
        self.toBeValidated = []


    def createInitialDummyBlock(self, addresses):
        transactions = []
        for address in addresses:
            initialTransaction = CmpETransaction(None, address, INITIAL_AMOUNT)
            transactions.append(initialTransaction)
        genesisBlock = CmpEBlock(0, transactions, None)
        self.chain.append(genesisBlock)
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
            print("Genesis block has no previous block.")
            return False
        for transaction in self.chain[0].transactions:
            if transaction.amount != INITIAL_AMOUNT or transaction.fromAddress != None:
                print("Genesis block wrong.")
                if returnWallet:
                    return False, dict()
                return False
            else:
                walletDict[transaction.toAddress.to_string().hex()] = walletDict.get(transaction.toAddress.to_string().hex(), 0) + INITIAL_AMOUNT                

        index = 1

        while index < len(self.chain):
            lastBlock = self.chain[index]

            lastBlockHash = lastBlock.currBlockHash

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

            if lastBlock.prevBlockHash != prevBlock.currBlockHash:
                logging.info("Chain is not properly linked.")
                if returnWallet:
                    return False, dict()
                return False

            fromNoneCount = 0 

            for transaction in lastBlock.transactions:
                if transaction.fromAddress == None and fromNoneCount == 0:
                    fromNoneCount = 1
                    continue
                elif transaction.fromAddress == None:
                    logging.info(f"Two rewards in one block, chain not valid.")
                    if returnWallet:
                        return False, dict()
                    return False
                
                currentWallet = walletDict.get(transaction.fromAddress.to_string().hex(), 0)
                if transaction.amount > currentWallet:
                    logging.info(f"{transaction.fromAddress.to_string().hex()} spent more than it has. Chain not valid.")
                    if returnWallet:
                        return False, dict()
                    return False
                walletDict[transaction.fromAddress.to_string().hex()] = walletDict.get(transaction.fromAddress.to_string().hex(), 0) - transaction.amount
            
            if fromNoneCount == 1 and len(lastBlock.transactions) == 1:
                logging.info(f"Block cannot only have reward. Chain not valid.")
                if returnWallet:
                    return False, dict()
                return False

            for transaction in lastBlock.transactions:
                walletDict[transaction.toAddress.to_string().hex()] = walletDict.get(transaction.toAddress.to_string().hex(), 0) + transaction.amount

            index = index + 1

        if returnWallet:
            return True, walletDict
        return True
 
    
    def addTransactionToPendingList(self, transx):
        if transx.isTransactionValid():
            self.pendingTransactions.append(transx)
            return True
        return False

    def validatePendingTransactions(self, rewardAddress, prevHash, tempList):

        tempList.append(CmpETransaction(None, rewardAddress, self.validationReward))
        
        newBlock = CmpEBlock(0, tempList, prevHash)

        newBlock.validateBlock(self.difficulty)
        self.toBeValidated = []
        return newBlock

    def getBalanceOf(self, address):
        balance = 0

        for transaction in self.getAllTransactionsFor(address):
            if transaction.fromAddress == address:
                balance -= transaction.amount
            if transaction.toAddress == address:
                balance += transaction.amount

        return balance

    def getAllTransactionsFor(self, address):
        transactions = []

        for block in self.chain:
            for transaction in block.transactions:
                if transaction.fromAddress == address or transaction.toAddress == address:
                    transactions.append(transaction)

        return transactions
