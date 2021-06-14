from threading import Thread, Lock
import pika
from blockchain import CmpEBlockchain 
from transaction import CmpETransaction
from wallet import CmpECoinWallet
import logging

class CmpECoinValidatorNode():

    def __init__(self, netwDispatcherAddress):
        self.blockchainMutex = Lock()
        self.wallet = CmpECoinWallet()
        self.netwDispatcherAddress = netwDispatcherAddress
        self.blockchain = CmpEBlockchain([])
        # Listen transactions
        transactionThread = Thread(target = self.listenForTransactions )
        # Listen validated blocks
        validationThread = Thread(target = self.listenForValidation)
        # Listen for validation beacon
        validationBeaconThread = Thread(target = self.listenForValidationBeacon)

    def listenForTransactions(self):
        parameters = pika.ConnectionParameters('localhost', 5672, '/', pika.PlainCredentials('user', 'password'))
        connection = pika.SelectConnection(parameters, on_open_callback=self.on_connected_transaction)

    def on_connected_transaction(self, connection):
        connection.channel(on_open_callback = self.on_channel_open_transaction)

    def on_channel_open_transaction(self, channel):
        channel.exchange_declare(exchange='dispatcherTransaction', exchange_type='fanout')
        channel.queue_declare(queue='transaction', exclusive=True)
        channel.queue_bind(exchange='dispatcherTransaction', queue='transaction')
        channel.basic_consume(queue='transaction', on_message_callback=self.handleReceivedTransactions, auto_ack=True)

    def listenForValidation(self):
        pass

    def listenForValidationBeacon(self):
        pass

    def joinCmpECoinNetw():
        pass

    def handleReceivedTransactions(self, channel, method, properties, body):
        transaction = self.parseBody(body)
        self.blockchainMutex.acquire()
        if self.blockchain.addTransactionToPendingList(transaction):
            logging.info(f'Validator Node {self.wallet.getPublicKey()} added a valid transaction to its pending transactions.')
            self.blockchainMutex.release()
            return True
        logging.info(f'Validator Node {self.wallet.getPublicKey()} received a invalid transaction.')
        self.blockchainMutex.release()
        return False

    def parseBody(self, body):
        return ""

    def handleReceivedValidatedBlock(self, channel, method, properties, body):
        block = self.parseBody(body)
        self.blockchainMutex.acquire()
        self.blockchain.append(block)
        if self.blockchain.isChainValid():
            logging.info(f'Validator Node {self.wallet.getPublicKey()} added a validated block to its blockchain.')
            self.blockchainMutex.release()
            return True
        self.blockchain.pop()
        logging.info(f'Validator Node {self.wallet.getPublicKey()} received an invalid block, did not add to its blockchain.')
        self.blockchainMutex.release()
        return False

    def handleBeaconAndStartValidationProc(self, channel, method, properties, body):
        message = self.parseBody(body)

        self.blockchain.validatePendingTransactions()
        # TODO: Open thread and send block to dispatcher


