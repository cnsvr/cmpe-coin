from block import CmpEBlock
from threading import Thread, Lock
import pika
import time
import random
import numpy as np
import logging
import json
from time import sleep
import binascii
from transaction import CmpETransaction


from ecdsa import SigningKey, SECP256k1, VerifyingKey

logging.getLogger("pika").setLevel(logging.WARNING)

class CmpECoinSimpleNode():
    def __init__(self, netwDispatcherAddress, blockChain, myWallet, meanTransactionInterDuration, meanTransactionAmount, listenQForValidatedBlocksFromNetwDispatcher):
        self.netwDisptcherAddress = netwDispatcherAddress
        self.blockChainMutex = Lock()
        self.blockChain = blockChain
        self.myWallet = myWallet
        self.PKsInNetwork = []
        self.meanTransactionInterDuration = meanTransactionInterDuration
        self.meanTransactionAmount = meanTransactionAmount
        self.listenQForValidatedBlocksFromNetwDispatcher = listenQForValidatedBlocksFromNetwDispatcher
        self.parameters = pika.ConnectionParameters(host=self.netwDisptcherAddress)

    def joinCmpECoinNetw(self):
        connection = pika.BlockingConnection(self.parameters)
        # Send self public key to dispatcher after connection is made.
        self.sendPublicKeyToDispatcher(connection, self.myWallet.getPublicKey())
        # Listen new simple nodes
        listenNewJoiningSimpleNodes = Thread(target=self.listenNewJoiningSimpleNodes)
        # Listen for new transactions (from 3rd party to self simple node) (for test/demo purposes)
        listenNewTransactionAndSendDistpatcher = Thread(target=self.listenNewTransactionAndSendDistpatcher)
        # Listen for validated blocks
        listenNewValidatedBlocks = Thread(target=self.validatedBlockConsumer)

        listenNewJoiningSimpleNodes.start()
        listenNewValidatedBlocks.start()
        listenNewTransactionAndSendDistpatcher.start()

    def sendPublicKeyToDispatcher(self, connection, public_key):
        channel = connection.channel()
        channel.queue_declare(queue='publicKeyRcvQ')
        channel.basic_publish(exchange='', routing_key='publicKeyRcvQ', body=public_key)

        print('Public key', public_key, ' is sent to:', self.netwDisptcherAddress)

    def validatedBlockConsumer(self):
        connection = pika.BlockingConnection(self.parameters)
        channel = connection.channel()
        channel.exchange_declare(exchange='dispatcherNewValidatedBlock', exchange_type='fanout')
        channel.queue_declare(queue='validatedBlock', exclusive=True)
        channel.queue_bind(exchange='dispatcherNewValidatedBlock', queue='validatedBlock')
        channel.basic_consume(queue='validatedBlock', on_message_callback=self.handleReceivedValidatedBlock, auto_ack=True)

        print('Starting listening for new validated blocks...')
        channel.start_consuming()

    def handleReceivedValidatedBlock(self, ch, method, properties, body):
        # log the block received as stringified json
        print('Received message # %s from %s: %s', method.delivery_tag, properties.app_id, body)
        # handle the block received
        body = self.convertJSONBlockToObject(body)
        # acquire blockchain to update
        self.blockChainMutex.acquire()
        self.blockChain.append(body)
        if not self.blockChain.isChainValid():
            print('Blockchain is not valid! Block is discarded...')
            self.blockChain.pop()
        else:
            print('Blockchain is valid, block is added to the blockchain.')
        # release blockchain
        self.blockChainMutex.release()
    
    def convertJSONBlockToObject(self, json_block):
        body = json.loads(json_block)
        block = None

        index = body['index']
        timestamp = body['timestamp']
        prevBlockHash = body['prevBlockHash']
        proofOfWork = body['proofOfWork']

        transactions = []
        for transaction in body.transactions:
            transactions.append(self.parseAndCreateTransaction(transaction))

        block = CmpEBlock(index, transactions, prevBlockHash, proofOfWork, timestamp=timestamp)
        
        # TODO(eridincu): Check if that ever happens
        # Validation check for block, logging purposes
        print('Created Block Hash == Received Block Hash? ---->', (block.currBlockHash == body['currBlockHash']))
        return block

    def doRandomTransactions(self):
        # make a new thread and create random transaction and join thread to main thread.
        while True:
            duration = np.random.exponential(self.meanTransactionInterDuration)
            
            # sleep for duration
            sleep(duration)
            
            # create a new thread and call newTransaction function.

            newTransactionThread = Thread(target = self.newValidTransaction)
            newTransactionThread.start()
            newTransactionThread.join()
    
    def doRandomInvalidTransaction(self):
        # make a new thread and create random transaction and join thread to main thread.
        while True:
            duration = np.random.exponential(self.meanTransactionInterDuration)
            
            # sleep for duration
            sleep(duration)
            
            # create a new thread and call newTransaction function.

            newTransactionThread = Thread(target = self.newInvalidTransaction)
            newTransactionThread.start()
            newTransactionThread.join()

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
        
        random_pk = random.choice(self.PKsInNetwork)
        transaction = CmpETransaction(self.myWallet.getPublicKey(), random_pk, amount)

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
        
        random_pk = random.choice(self.PKsInNetwork)
        transaction = CmpETransaction(self.myWallet.getPublicKey(), random_pk, amount)

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
        connection = pika.BlockingConnection(self.parameters)      
        channel = connection.channel()
        channel.queue_declare(queue='transxRcvQ')
        channel.basic_publish(exchange='',
                      routing_key='transxRcvQ',
                      body=transaction_json)

    # Create a connection and listen transaction from this node, create a transaction and send to dispatcher ??


    def listenNewJoiningSimpleNodes(self):
        connection = pika.BlockingConnection(self.parameters)
        channel = connection.channel()
        channel.exchange_declare(exchange='dispatcherNewSimpleNode', exchange_type='fanout')
        channel.queue_declare(queue='simpleNode', exclusive=True)
        channel.queue_bind(exchange='dispatcherNewSimpleNode', queue='simpleNode')
        channel.basic_consume(queue='simpleNode', on_message_callback=self.handleReceivedSimpleNode, auto_ack=True)

        print('Starting to listen for new joining simple nodes...')
        channel.start_consuming()

    def handleReceivedSimpleNode(self, channel, method, properties, body):
        response = json.loads(body)
        type = response['type']
        pk = response['pk']
        
        if type == 0 and pk != self.myWallet.getPublicKey(): # it means type 0 belongs to simple node.
            self.PKsInNetwork.append(pk)
            return True
        return False
    
    def listenNewTransactionAndSendDistpatcher(self):
        connection = pika.BlockingConnection(self.parameters)
        channel = connection.channel()
        channel.exchange_declare(exchange='dispatcherNewTransaction', exchange_type='fanout')
        channel.queue_declare(queue='transaction', exclusive=True)
        channel.queue_bind(exchange='dispatcherNewTransaction', queue='transaction')
        channel.basic_consume(queue='transaction', on_message_callback=self.handleReceivedTransaction, auto_ack=True)
        
        print('Starting to listen for transactions from third party users (for test/demo purposes)... ')
        channel.start_consuming()

    def handleReceivedTransaction(self, channel, method, properties, body):
        transaction = self.parseAndCreateTransaction(body)        
        if transaction:
            # send to transaction to dispatcher
            # Convert to transaction to Json format
            transaction_json=transaction.toJSON()
            # send the json to node.
            self.sendTransactionToDispatcher(transaction_json)
            return True
        return False

    def parseAndCreateTransaction(self, payload):
        body = json.loads(payload)
        transaction = None
        
        if body['fromAddress'] == self.myWallet.getPublicKey().to_string().hex():
            fromAddress = VerifyingKey.from_string(bytes.fromhex(body['fromAddress']), curve=SECP256k1)
            toAddress = VerifyingKey.from_string(bytes.fromhex(body['toAddress']), curve=SECP256k1)
            amount = body['amount']
            transaction = CmpETransaction(fromAddress, toAddress, amount, False)
            transaction.signTransaction(self.myWallet.getPrivateKey())

        return transaction