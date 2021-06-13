class CmpECoinSimpleNode():
    def __init__(self, netwDispatcherAddress, blockChain, myWallet, meanTransactionInterDuration, meanTransactionAmount, listenQForValidatedBlocksFromNetwDispatcher):
        self.netwDisptcherAddress = netwDispatcherAddress
        self.blockChain = blockChain
        self.myWallet = myWallet
        self.meanTransactionInterDuration = meanTransactionInterDuration
        self.meanTransactionAmount = meanTransactionAmount
        self.listenQForValidatedBlocksFromNetwDispatcher = listenQForValidatedBlocksFromNetwDispatcher

    # erdinc
    def joinCmpECoinNetw(self):
        pass

    def handleReceivedValidatedBlock(self):
        pass
    
    # furkan
    def doRandomTransactions(self):
        pass

    def doRandomInvalidTransaction(self):
        pass

