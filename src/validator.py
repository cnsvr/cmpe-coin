import json
from threading import Thread, Lock
import pika
from src.blockchain import CmpEBlockchain
from src.transaction import CmpETransaction
from src.block import CmpEBlock
from src.wallet import CmpECoinWallet
import logging


class CmpECoinValidatorNode():

    def __init__(self, netwDispatcherAddress):
        self.blockchainMutex = Lock()
        self.wallet = CmpECoinWallet()
        self.netwDispatcherAddress = netwDispatcherAddress
        self.blockchain = CmpEBlockchain([])
        # Listen transactions
        transactionThread = Thread(target=self.listenForTransactions)
        # Listen validated blocks
        validatedBlocksThread = Thread(target=self.listenForValidatedBlocks)
        # Listen for validation beacon
        validationBeaconThread = Thread(target=self.listenForValidationBeacon)

        self.parameters = pika.ConnectionParameters('localhost', 5672, '/', pika.PlainCredentials('user', 'password'))

    def listenForTransactions(self):

        connection = pika.SelectConnection(self.parameters, on_open_callback=self.on_connected_transaction)
        channel = connection.channel(on_open_callback=self.on_channel_open_transaction)
        channel.exchange_declare(exchange='dispatcherTransaction', exchange_type='fanout')
        channel.queue_declare(queue='transaction', exclusive=True)
        channel.queue_bind(exchange='dispatcherTransaction', queue='transaction')
        channel.basic_consume(queue='transaction', on_message_callback=self.handleReceivedTransactions, auto_ack=True)
        try:
            # Loop so we can communicate with RabbitMQ
            connection.ioloop.start()
        except KeyboardInterrupt:
            # Gracefully close the connection
            connection.close()
            # Loop until we're fully closed, will stop on its own
            connection.ioloop.start()
        channel.start_consuming()

    def listenForValidatedBlocks(self):

        connection = pika.SelectConnection(self.parameters, on_open_callback=self.on_connected_transaction)
        channel = connection.channel(on_open_callback=self.on_channel_open_transaction)
        channel.exchange_declare(exchange='dispatcherValidatedBlocks', exchange_type='fanout')
        channel.queue_declare(queue='blocks', exclusive=True)
        channel.queue_bind(exchange='dispatcherValidatedBlocks', queue='blocks')
        channel.basic_consume(queue='blocks', on_message_callback=self.handleReceivedValidatedBlock, auto_ack=True)
        try:
            # Loop so we can communicate with RabbitMQ
            connection.ioloop.start()
        except KeyboardInterrupt:
            # Gracefully close the connection
            connection.close()
            # Loop until we're fully closed, will stop on its own
            connection.ioloop.start()
        channel.start_consuming()

    def listenForValidationBeacon(self):

        connection = pika.SelectConnection(self.parameters, on_open_callback=self.on_connected_transaction)
        channel = connection.channel(on_open_callback=self.on_channel_open_transaction)
        channel.exchange_declare(exchange='dispatcherValidationBeacon', exchange_type='fanout')
        channel.queue_declare(queue='beacon', exclusive=True)
        channel.queue_bind(exchange='dispatcherValidationBeacon', queue='beacon')
        channel.basic_consume(queue='beacon', on_message_callback=self.handleBeaconAndStartValidationProc,
                              auto_ack=True)
        try:
            # Loop so we can communicate with RabbitMQ
            connection.ioloop.start()
        except KeyboardInterrupt:
            # Gracefully close the connection
            connection.close()
            # Loop until we're fully closed, will stop on its own
            connection.ioloop.start()
        channel.start_consuming()

    def joinCmpECoinNetw(self):
        connection = pika.SelectConnection(self.parameters, on_open_callback=self.on_connected_transaction)
        channel = connection.channel(on_open_callback=self.on_channel_open_transaction)
        channel.queue_declare(queue='joinCmpECoinNetw')
        channel.basic_publish(exchange='',
                              routing_key='joinCmpECoinNetw',
                              body='join')
        channel.basic_consume(queue='joinCmpECoinNetw', on_message_callback=self.handleRecievedBlockchain,
                              auto_ack=True)
        pass

    def handleRecievedBlockchain(self, channel, method, properties, body):
        self.blockChain = self.parseBlockChain(body)

    def handleReceivedTransactions(self, channel, method, properties, body):
        transaction = self.parseTransaction(body)
        self.blockchainMutex.acquire()
        if self.blockchain.addTransactionToPendingList(transaction):
            logging.info(
                f'Validator Node {self.wallet.getPublicKey()} added a valid transaction to its pending transactions.')
            self.blockchainMutex.release()
            return True
        logging.info(f'Validator Node {self.wallet.getPublicKey()} received an invalid transaction.')
        self.blockchainMutex.release()
        return False

    def parseBody(self, body):
        return ""

    def handleReceivedValidatedBlock(self, channel, method, properties, body):
        block = self.parseBlock(body)
        self.blockchainMutex.acquire()
        self.blockchain.append(block)
        if self.blockchain.isChainValid():
            logging.info(f'Validator Node {self.wallet.getPublicKey()} added a validated block to its blockchain.')
            self.blockchainMutex.release()
            return True
        self.blockchain.pop()
        logging.info(
            f'Validator Node {self.wallet.getPublicKey()} received an invalid block, did not add to its blockchain.')
        self.blockchainMutex.release()
        return False

    def handleBeaconAndStartValidationProc(self, channel, method, properties, body):
        message = self.parseBody(body)

        newBlock = self.blockchain.validatePendingTransactions(3)
        # TODO: Open thread and send block to dispatcher
        sendBlockToDispatcher = Thread(target=self.sendValidatedBlock, args=(newBlock.json(),))

    def sendValidatedBlock(self, blockJson):

        connection = pika.SelectConnection(self.parameters, on_open_callback=self.on_connected_transaction)
        channel = connection.channel(on_open_callback=self.on_channel_open_transaction)
        channel.exchange_declare(exchange='validatedBlockToDispatcher', exchange_type='fanout')
        channel.basic_publish('validatedBlockToDispatcher',
                              '',
                              blockJson,
                              pika.BasicProperties(content_type='text/plain',
                                                   type='example'))

    def parseBlock(self, body):
        blockJson = json.loads(body)
        transactions = []

        for transactionJson in blockJson.transactions:
            transaction = CmpETransaction(transactionJson.fromAddress, transactionJson.toAddress,
                                          transactionJson.amount)
            transactions.append(transaction)

        return CmpEBlock(None, transactions, blockJson.prevHashBlock, blockJson.proofOfWork, blockJson.timestamp)

    def parseTransaction(self, body):
        transactionJson = json.load(body)
        return CmpETransaction(transactionJson.fromAddress, transactionJson.toAddress, transactionJson.amount)
