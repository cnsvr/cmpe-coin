import json
from threading import Thread, Lock
import pika
from blockchain import CmpEBlockchain
from transaction import CmpETransaction
from block import CmpEBlock
from CmpECoinWallet import CmpECoinWallet
import logging
import os
from dotenv import load_dotenv
from ecdsa import SigningKey, VerifyingKey
import ecdsa

load_dotenv()

class CmpECoinValidatorNode():

    def __init__(self):
        print("Validator Node Initialized")
        self.blockchainMutex = Lock()
        self.wallet = CmpECoinWallet()
        self.wallet.initWallet()
        self.blockchain = CmpEBlockchain([])
        self.parameters = pika.ConnectionParameters('localhost', 5672, '/', pika.PlainCredentials('user', 'password'))
        # Listen transactions
        transactionThread = Thread(target=self.listenForTransactions)
        # Listen validated blocks
        validatedBlocksThread = Thread(target=self.listenForValidatedBlocks)
        # Listen for validation beacon
        validationBeaconThread = Thread(target=self.listenForValidationBeacon)

        transactionThread.start()
        validatedBlocksThread.start()
        validationBeaconThread.start()

        

    def listenForTransactions(self):

        connection = pika.BlockingConnection(self.parameters)
        channel = connection.channel()
        channel.exchange_declare(exchange= os.getenv("TRANSX_EXCHANGE"), exchange_type='fanout')
        queue_name = 'transaction'+self.wallet.getPublicKey().to_string().hex()  
        channel.queue_declare(queue=queue_name, exclusive=True)
        channel.queue_bind(exchange= os.getenv("TRANSX_EXCHANGE"), queue=queue_name)
        channel.basic_consume(queue=queue_name, on_message_callback=self.handleReceivedTransactions, auto_ack=True)
        
        channel.start_consuming()

    def listenForValidatedBlocks(self):

        connection = pika.BlockingConnection(self.parameters)
        channel = connection.channel()
        channel.exchange_declare(exchange = os.getenv("BLOCK_EXCHANGE"), exchange_type='fanout')
        queue_name = 'blocks'+self.wallet.getPublicKey().to_string().hex()  
        channel.queue_declare(queue=queue_name, exclusive=True)
        channel.queue_bind(exchange = os.getenv("BLOCK_EXCHANGE"), queue=queue_name)
        channel.basic_consume(queue=queue_name, on_message_callback=self.handleReceivedValidatedBlock, auto_ack=True)
        
        channel.start_consuming()

    def listenForValidationBeacon(self):

        connection = pika.BlockingConnection(self.parameters)
        channel = connection.channel()
        channel.exchange_declare(exchange=os.getenv("VALIDATION_BEACON"), exchange_type='fanout')
        queue_name = 'beacon'+self.wallet.getPublicKey().to_string().hex()   
        channel.queue_declare(queue=queue_name, exclusive=True)
        channel.queue_bind(exchange=os.getenv("VALIDATION_BEACON"), queue=queue_name)
        channel.basic_consume(queue=queue_name, on_message_callback=self.handleBeaconAndStartValidationProc,
                              auto_ack=True)
        
        channel.start_consuming()

    def joinCmpECoinNetw(self):
        connection = pika.BlockingConnection(self.parameters)
        channel = connection.channel()
        channel.queue_declare(queue=os.getenv("JOIN_QUEUE"))
        body = {
            "type": 0,
            "pk": self.wallet.getPublicKey().to_string().hex() 
        }
        channel.basic_publish(exchange='',
                              routing_key='joinCmpECoinNetw',
                              body=body)
        channel.basic_consume(queue='joinCmpECoinNetw', on_message_callback=self.handleRecievedBlockchain,
                              auto_ack=True)
        pass

    def handleRecievedBlockchain(self, channel, method, properties, body):
        self.blockChain = self.parseBlockChain(body)

    def handleReceivedTransactions(self, channel, method, properties, body):
        transaction = self.parseTransaction(body)
        self.blockchainMutex.acquire()
        if self.blockchain.addTransactionToPendingList(transaction):
            print(
                f'Validator Node {self.wallet.getPublicKey().to_string().hex()[0:10]}: added a valid transaction to its pending transactions.')
            self.blockchainMutex.release()
            return True
        print(f'Validator Node {self.wallet.getPublicKey().to_string().hex()[0:10]}: received an invalid transaction with hash {transaction.hash}')
        self.blockchainMutex.release()
        return False

    def parseBody(self, body):
        return ""

    def handleReceivedValidatedBlock(self, channel, method, properties, body):
        block = self.parseBlock(body)
        self.blockchainMutex.acquire()
        self.blockchain.chain.append(block)
        if self.blockchain.isChainValid():
            print(f'Validator Node {self.wallet.getPublicKey().to_string().hex()[0:10]}: added a validated block to its blockchain.')
            block.transactions.sort(key=lambda x: x.timestamp, reverse=True)
            lastTimestamp = block.transactions[0].timestamp
            for transaction in self.blockchain.pendingTransactions:
                if transaction.timestamp < lastTimestamp and transaction in self.blockchain.pendingTransactions :
                    self.blockchain.pendingTransactions.remove(transaction)
            self.blockchainMutex.release()
            return True
        self.blockchain.chain.pop()
        print(
            f'Validator Node {self.wallet.getPublicKey().to_string().hex()[0:10]}: received an invalid block, did not add to its blockchain.')
        self.blockchainMutex.release()
        return False

    def handleBeaconAndStartValidationProc(self, channel, method, properties, body):
        message = self.parseBody(body)
        self.blockchainMutex.acquire()
        isValid, walletDict = self.blockchain.isChainValid(True)
        if not isValid:
            #logging.info(
            #f'Validator Node {self.wallet.getPublicKey().to_string().hex()} has a non-valid blockchain.')
            return False
        for transaction in self.blockchain.pendingTransactions:
            # Can not have reward on non-validated 
            if transaction.fromAddress == None:
                self.blockchain.pendingTransactions.remove(transaction)
                continue
            currentWallet = walletDict.get(transaction.fromAddress.to_string().hex(), 0)
            if transaction.amount > currentWallet:
                self.blockchain.pendingTransactions.remove(transaction)
            else:
                walletDict[transaction.fromAddress.to_string().hex()] = walletDict.get(transaction.fromAddress.to_string().hex(), 0) - transaction.amount
    
        # should pendings removed when waiting new 
        self.blockchain.toBeValidated = self.blockchain.pendingTransactions
        self.blockchain.pendingTransactions = []
        self.blockchainMutex.release()
        newBlock = self.blockchain.validatePendingTransactions(self.wallet.getPublicKey())
        # TODO: Open thread and send block to dispatcher
        sendBlockToDispatcher = Thread(target=self.sendValidatedBlock, args=(newBlock.toJSON(),))
        sendBlockToDispatcher.start()

    def sendValidatedBlock(self, blockJson):
        print(f'Validator Node {self.wallet.getPublicKey().to_string().hex()[0:10]}: found an proof of work.')
        connection = pika.BlockingConnection(self.parameters)
        channel = connection.channel()
        channel.queue_declare(queue = os.getenv("VALIDATED_TO_DISP"))
        #channel.exchange_declare(exchange='validatedBlockToDispatcher', exchange_type='fanout')
        channel.basic_publish('',
                              os.getenv("VALIDATED_TO_DISP"),
                              blockJson,
                              pika.BasicProperties(content_type='text/plain',
                                                   type='example'))

    def parseBlock(self, body):
        blockJson = json.loads(body.decode())
        transactions = []

        for transactionT in blockJson["transactions"]:
            transactionJson = json.loads(transactionT)
            fromAddress = VerifyingKey.from_string(bytes.fromhex(transactionJson["fromAddress"]), curve=ecdsa.SECP256k1) if transactionJson["fromAddress"] else None
            toAddress = VerifyingKey.from_string(bytes.fromhex(transactionJson["toAddress"]), curve=ecdsa.SECP256k1)
            transaction = CmpETransaction(fromAddress, toAddress,
                                          transactionJson["amount"])
            transaction.timestamp = transactionJson["timestamp"]
            transaction.hash = transactionJson["hash"]
            transaction.signature = transactionJson["signature"]

            transactions.append(transaction)

        return CmpEBlock(0, transactions, blockJson["prevBlockHash"], blockJson["proofOfWork"], blockJson["timestamp"])

    def parseTransaction(self, body):
        body = json.loads(body)
        fromAddress = VerifyingKey.from_string(bytes.fromhex(body['fromAddress']), curve=ecdsa.SECP256k1)
        toAddress = VerifyingKey.from_string(bytes.fromhex(body['toAddress']), curve=ecdsa.SECP256k1)
        amount = body['amount']
        timestamp = body['timestamp']
        hash = body['hash']
        signature = bytes.fromhex(body['signature'])  if body["signature"] else None

        transaction = CmpETransaction(fromAddress, toAddress, amount, False)
        transaction.timestamp = timestamp
        transaction.hash = hash
        transaction.signature = signature

        return transaction
