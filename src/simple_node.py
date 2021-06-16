from threading import Thread, Lock
import pika
import time
import numpy as np
import logging
import json
from time import sleep
import binascii
from transaction import CmpETransaction

from ecdsa import SigningKey, SECP256k1, VerifyingKey

sk_N = SigningKey.generate(curve=SECP256k1)
pk_N = sk_N.verifying_key



class CmpECoinSimpleNode():
    def __init__(self, netwDispatcherAddress, blockChain, myWallet, meanTransactionInterDuration, meanTransactionAmount, listenQForValidatedBlocksFromNetwDispatcher):
        self.netwDisptcherAddress = netwDispatcherAddress
        self.blockChainMutex = Lock()
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
    

    def doRandomTransactions(self):
        # make a new thread and create random transaction and join thread to main thread.
        while True:
            duration = np.random.exponential(self.meanTransactionInterDuration)
            
            # sleep for duration
            sleep(duration)
            
            # create a new thread and call newTransaction function.

            newTransactionThread = Thread(target = self.newValidTransaction)
            # newTransactionThread.start()
            # newTransactionThread.join()
    
    def doRandomInvalidTransaction(self):
        # make a new thread and create random transaction and join thread to main thread.
        while True:
            duration = np.random.exponential(self.meanTransactionInterDuration)
            
            # sleep for duration
            sleep(duration)
            
            # create a new thread and call newTransaction function.

            newTransactionThread = Thread(target = self.newInvalidTransaction)
            # newTransactionThread.start()
            # newTransactionThread.join()

    def newValidTransaction(self):
        # Get the my current balance from blockchain.
        self.blockChainMutex.acquire()
        my_current_balance = self.blockChain.getBalance(self.myWallet.getPublicKey())
        self.blockChainMutex.release()

        self.myWallet.setCurrentBalance(my_current_balance)
        amount = np.random.exponential(self.meanTransactionAmount)

        # Find enough amount for valid transaction
        while my_current_balance < amount:
            amount = np.random.exponential(self.meanTransactionAmount)
        
        transaction = CmpETransaction(self.myWallet.getPublicKey(), pk_N, amount)

        # Sign the transaction before sending it to the node.
        if transaction.signTransaction(self.myWallet.getPrivateKey()):
            # Transaction is valid
            self.myWallet.setCurrentBalance(self.myWallet.getCurrentBalance() -  amount)
            # Convert to transaction to Json format
            transaction_json=transaction.toJSON()
            # send the json to node.
            self.sendTransactionToDispatcher(transaction_json)
            return True
        else:
            return False

    def newInvalidTransaction(self):
        # Get the my current balance from blockchain.
        self.blockChainMutex.acquire()
        my_current_balance = self.blockChain.getBalance(self.myWallet.getPublicKey())
        self.blockChainMutex.release()

        self.myWallet.setCurrentBalance(my_current_balance)
        amount = np.random.exponential(self.meanTransactionAmount)

        # Find enough amount for valid transaction
        while my_current_balance < amount:
            amount = np.random.exponential(self.meanTransactionAmount)
        
        transaction = CmpETransaction(self.myWallet.getPublicKey(), pk_N, amount)

        # Sign the transaction before sending it to the node.
        if transaction.signTransaction(self.myWallet.getPrivateKey()):
            # Transaction is valid
            self.myWallet.setCurrentBalance(self.myWallet.getCurrentBalance() -  amount)

            # Change amount and timestamp of transaction to make invalid.

            transaction.amount = np.random.exponential(self.meanTransactionAmount) ** 2
            transaction.timestamp = time.time()

            # Convert to transaction to Json format
            transaction_json=transaction.toJSON()
            # send the json to node.
            self.sendTransactionToDispatcher(transaction_json)
            return True
        else:
            return False
    
    def sendTransactionToDispatcher(self, transaction_json):
        connection = pika.SelectConnection(self.parameters)        
        channel = connection.channel()
        channel.queue_declare(queue='transxRcvQ')
        channel.basic_publish(exchange='',
                      routing_key='transxRcvQ',
                      body=transaction_json)



'''
transaction = CmpETransaction(pk_N, pk_N, 200, False)
transaction.signTransaction(sk_N)

transaction_json = transaction.toJSON()

connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))        
channel = connection.channel()
channel.queue_declare(queue='transxRcvQ')
channel.basic_publish(exchange='',
                routing_key='transxRcvQ',
                body=transaction_json)
'''