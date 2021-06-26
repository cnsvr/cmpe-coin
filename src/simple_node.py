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
from CmpECoinWallet import CmpECoinWallet
from blockchain import CmpEBlockchain
from ecdsa import SigningKey, SECP256k1, VerifyingKey
import os
import ecdsa
from dotenv import load_dotenv

load_dotenv()

logging.getLogger("pika").setLevel(logging.WARNING)

class CmpECoinSimpleNode():
    def __init__(self, wallet, meanTransactionInterDuration, meanTransactionAmount, PKsInNetwork = []):
        print("Simple Node Initialized")
        self.blockChainMutex = Lock()
        self.blockChain = CmpEBlockchain([])
        self.wallet = wallet
        self.PKsInNetwork = PKsInNetwork.copy()
        self.PKsInNetwork.remove(self.wallet.getPublicKey())
        self.meanTransactionInterDuration = meanTransactionInterDuration
        self.meanTransactionAmount = meanTransactionAmount
        self.parameters = pika.ConnectionParameters('localhost', 5672, '/', pika.PlainCredentials('user', 'password'))
        self.joinCmpECoinNetw()

    


    def joinCmpECoinNetw(self):
        connection = pika.BlockingConnection(self.parameters)
        # Send self public key to dispatcher after connection is made.
        self.sendPublicKeyToDispatcher(connection, self.wallet.getPublicKey())
        # Listen new simple nodes
        listenNewJoiningSimpleNodes = Thread(target=self.listenNewJoiningSimpleNodes)
        # Listen for new transactions (from 3rd party to self simple node) (for test/demo purposes)
        listenNewTransactionAndSendDistpatcher = Thread(target=self.listenNewTransactionAndSendDistpatcher)
        # Listen for validated blocks
        listenNewValidatedBlocks = Thread(target=self.validatedBlockConsumer)
        
        doRandomInvalidTransaction = Thread(target = self.doRandomInvalidTransaction)
        doRandomTransactions = Thread(target =self.doRandomTransactions)

        listenNewJoiningSimpleNodes.start()
        listenNewValidatedBlocks.start()
        listenNewTransactionAndSendDistpatcher.start()
        doRandomInvalidTransaction.start()
        doRandomTransactions.start()

    def sendPublicKeyToDispatcher(self, connection, public_key):
        channel = connection.channel()
        channel.queue_declare(queue=os.getenv("JOIN_QUEUE"))
        #channel.queue_declare(queue='publicKeyRcvQ')
        channel.basic_publish(exchange='', routing_key=os.getenv("JOIN_QUEUE"), body=public_key.to_string().hex())

        print('Public key', public_key.to_string().hex(), ' is sent to dispatcher')

    def validatedBlockConsumer(self):
        connection = pika.BlockingConnection(self.parameters)
        channel = connection.channel()
        channel.exchange_declare(exchange = os.getenv("BLOCK_EXCHANGE"), exchange_type='fanout')
        queue_name = 'blocks'+self.wallet.getPublicKey().to_string().hex() 
        channel.queue_declare(queue=queue_name, exclusive=True)
        channel.queue_bind(exchange=os.getenv("BLOCK_EXCHANGE"), queue=queue_name)
        channel.basic_consume(queue=queue_name, on_message_callback=self.handleReceivedValidatedBlock, auto_ack=True)

        print('Starting listening for new validated blocks...')
        channel.start_consuming()

    def handleReceivedValidatedBlock(self, ch, method, properties, body):
        print(f"Simple node {self.wallet.getPublicKey().to_string().hex()[0:10]}: Received a validated block.")
        # log the block received as stringified json
        #print('Received message # %s from %s: %s', method.delivery_tag, properties.app_id, body)
        # handle the block received
        body = self.parseBlock(body)
        # acquire blockchain to update
        self.blockChainMutex.acquire()
        self.blockChain.chain.append(body)
        if not self.blockChain.isChainValid():
            print(f'Simple node {self.wallet.getPublicKey().to_string().hex()[0:10]}: Blockchain is not valid! Block is discarded...')
            self.blockChain.chain.pop()
        else:
            print(f'Simple node {self.wallet.getPublicKey().to_string().hex()[0:10]}: Blockchain is valid, block is added to the blockchain.')
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

    def parseBlock(self, body):
        blockJson = json.loads(body)
        transactions = []

        for transactionT in blockJson["transactions"]:
            transactionJson = json.loads(transactionT)
            fromAddress = VerifyingKey.from_string(bytes.fromhex(transactionJson["fromAddress"]), curve=ecdsa.SECP256k1) if transactionJson["fromAddress"] else None
            toAddress = VerifyingKey.from_string(bytes.fromhex(transactionJson["toAddress"]), curve=ecdsa.SECP256k1)
            transaction = CmpETransaction(fromAddress, toAddress,
                                          transactionJson["amount"])
            transactions.append(transaction)

        return CmpEBlock(0, transactions, blockJson["prevBlockHash"], blockJson["proofOfWork"], blockJson["timestamp"])

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
        my_current_balance = self.blockChain.getBalanceOf(self.wallet.getPublicKey())
        self.blockChainMutex.release()
        self.wallet.setCurrentBalance(my_current_balance)
        if my_current_balance == 0:
            return True
        amount = np.random.exponential(self.meanTransactionAmount)

        # Find enough amount for valid transaction
        while my_current_balance < amount:
            amount = np.random.exponential(self.meanTransactionAmount)
        
        random_pk = random.choice(self.PKsInNetwork)
        transaction = CmpETransaction(self.wallet.getPublicKey(), random_pk, amount)

        # Sign the transaction before sending it to the node.
        if transaction.signTransaction(self.wallet.getPrivateKey()):
            # Transaction is valid
            self.wallet.setCurrentBalance(self.wallet.getCurrentBalance() -  amount)
            # Convert to transaction to Json format
            transaction_json=transaction.toJSON()
            # send the json to node.
            print(f'Simple node {self.wallet.getPublicKey().to_string().hex()[0:10]}: created an valid transaction with hash {transaction.hash} from {transaction.signature.hex()}.')
            self.sendTransactionToDispatcher(transaction_json)
            return True
        else:
            return False

    def newInvalidTransaction(self):
    # Get the my current balance from blockchain.
        self.blockChainMutex.acquire()
        my_current_balance = self.blockChain.getBalanceOf(self.wallet.getPublicKey())
        self.blockChainMutex.release()

        self.wallet.setCurrentBalance(my_current_balance)
        amount = np.random.exponential(self.meanTransactionAmount)

        # Find enough amount for valid transaction
        while my_current_balance < amount:
            amount = np.random.exponential(self.meanTransactionAmount)
        
        random_pk = random.choice(self.PKsInNetwork)
        transaction = CmpETransaction(self.wallet.getPublicKey(), random_pk, amount)

        # Sign the transaction before sending it to the node.
        if transaction.signTransaction(self.wallet.getPrivateKey()):
            # Transaction is valid
            self.wallet.setCurrentBalance(self.wallet.getCurrentBalance() -  amount)

            # Change amount and timestamp of transaction to make invalid.

            transaction.amount = np.random.exponential(self.meanTransactionAmount) ** 2
            transaction.timestamp = time.time()

            # Convert to transaction to Json format
            transaction_json=transaction.toJSON()
            # send the json to node.
            print(f'Simple node {self.wallet.getPublicKey().to_string().hex()[0:10]}: created an invalid transaction with hash {transaction.hash} from {transaction.signature.hex()}.')
            self.sendTransactionToDispatcher(transaction_json)
            return True
        else:
            return False


    
    def sendTransactionToDispatcher(self, transaction_json):
        connection = pika.BlockingConnection(self.parameters)      
        channel = connection.channel()
        channel.queue_declare(queue='newTransx')
        channel.basic_publish(exchange='',
                      routing_key='newTransx',
                      body=transaction_json)

    # Create a connection and listen transaction from this node, create a transaction and send to dispatcher ??


    def listenNewJoiningSimpleNodes(self):
        connection = pika.BlockingConnection(self.parameters)
        channel = connection.channel()
        channel.exchange_declare(exchange='dispatcherNewSimpleNode', exchange_type='fanout')
        queue_name = 'simpleNode' + self.wallet.getPublicKey().to_string().hex() 
        channel.queue_declare(queue=queue_name, exclusive=True)
        channel.queue_bind(exchange='dispatcherNewSimpleNode', queue=queue_name)
        channel.basic_consume(queue=queue_name, on_message_callback=self.handleReceivedSimpleNode, auto_ack=True)

        print('Starting to listen for new joining simple nodes...')
        channel.start_consuming()

    def handleReceivedSimpleNode(self, channel, method, properties, body):
        response = json.loads(body)
        type = response['type']
        pk = response['pk']
        
        if type == 0 and pk != self.wallet.getPublicKey().to_string().hex() : # it means type 0 belongs to simple node.
            self.PKsInNetwork.append(pk)
            return True
        return False
    
    def listenNewTransactionAndSendDistpatcher(self):
        connection = pika.BlockingConnection(self.parameters)
        channel = connection.channel()
        #channel.exchange_declare(exchange='dispatcherNewTransaction', exchange_type='fanout')
        queue_name = 'transaction'+self.wallet.getPublicKey().to_string().hex() 
        channel.queue_declare(queue=queue_name, exclusive=True)
        #channel.queue_bind(exchange='dispatcherNewTransaction', queue='transaction')
        channel.basic_consume(queue=queue_name, on_message_callback=self.handleReceivedTransaction, auto_ack=True)
        #channel.basic_consume(queue='transaction', on_message_callback=self.handleReceivedTransaction, auto_ack=True)
        print(f'Simple node {self.wallet.getPublicKey().to_string().hex()[0:10]}: Starting to listen for transactions from third party users (for test/demo purposes)...')
        #print('Starting to listen for transactions from third party users (for test/demo purposes)... ')
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
        
        if body['fromAddress'] == self.wallet.getPublicKey().to_string().hex():
            fromAddress = VerifyingKey.from_string(bytes.fromhex(body['fromAddress']), curve=SECP256k1)
            toAddress = VerifyingKey.from_string(bytes.fromhex(body['toAddress']), curve=SECP256k1)
            amount = body['amount']
            transaction = CmpETransaction(fromAddress, toAddress, amount, False)
            transaction.signTransaction(self.wallet.getPrivateKey())

        return transaction