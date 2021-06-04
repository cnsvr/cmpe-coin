import logging

class CmpEBlockchain:
    def __init__(self, chain, pendingTransactions = [], validationReward=1, difficulty=20):
        self.chain = chain 
        self.pendingTransactions = pendingTransactions
        self.validationReward = validationReward
        self.difficulty = difficulty


    def createInitialDummyBlock():
        pass
