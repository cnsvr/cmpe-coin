import logging
import block

class CmpEBlockchain:
    def __init__(self, chain, pendingTransactions=[], validationReward=1, difficulty=20):
        self.chain = chain
        self.pendingTransactions = pendingTransactions
        self.validationReward = validationReward
        self.difficulty = difficulty

    def createInitialDummyBlock():
        pass
    
    def addTransactionToPendingList(transx):
        this.pendingTransactions.append(transx)
    
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
