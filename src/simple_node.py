from os import truncate
import numpy as np
import logging
import _thread
import pika
import json
from time import process_time
import binascii
from transaction import CmpETransaction

from ecdsa import SigningKey, SECP256k1, VerifyingKey

sk_N = SigningKey.generate(curve=SECP256k1)
pk_N = sk_N.verifying_key



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
        def newTransaction(self):
            # Get the my current balance from blockchain.
            my_current_balance = self.blockChain.getBalance(self.myWallet.getPublicKey())
            self.myWallet.setCurrentBalance(my_current_balance)
            amount = np.random.exponential(self.meanTransactionAmount)

            # Find enough amount for valid transaction
            while my_current_balance < amount:
                amount = np.random.exponential(self.meanTransactionAmount)
            
            transaction = CmpETransaction(self.myWallet.getPublicKey(), pk_N, amount)

            if transaction.signTransaction(self.myWallet.getPrivateKey()):
                # Transaction is valid
                self.myWallet.setCurrentBalance(self.myWallet.getCurrentBalance() -  amount)
                # Connect to Validation Node and send the transaction.
                # connection = pika.BlockingConnection(pika.ConnectionParameters(self.netwDispatcherAddress))
                # channel = connection.channel()
                # channel.queue_declare(queue='transactions')
                transaction_json=transaction.toJSON()
                # send the json to node.
                
            else:
                return False

        # make a new thread and create random transaction and join thread to main thread.
        while True:
            duration = np.random.exponential(self.meanTransactionInterDuration)
            random_transaction_time = process_time()
            # wait for duration
            while process_time() - random_transaction_time < duration:
                pass
                # logging.info("Wait for making a new transaction")
            
            # create a new thread and call newTransaction function.
        
    def doRandomInvalidTransaction(self):
        pass

