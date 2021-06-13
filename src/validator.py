import threading
import pika

class CmpECoinValidatorNode():

    def __init__(self):
        # Listen transactions
        transactionThread = threading.Thread(target = self.listenForTransactions)
        # Listen validated blocks
        validationThread = threading.Thread(target = self.listenForValidation)
        # Listen for validation beacon
        validationThread = threading.Thread(target = self.listenForValidation)

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

    def joinCmpECoinNetw():
        pass

    def handleReceivedTransactions(self, channel, method, properties, body):
        pass

    def handleReceivedValidatedBlock(self):
        pass

    def handleBeaconAndStartValidationProc(self):
        pass

