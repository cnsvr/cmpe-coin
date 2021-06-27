#!/usr/bin/env python
import pika, sys, os, threading
from blockchain import CmpEBlockchain
from transaction import CmpETransaction
from block import CmpEBlock
from threading import Thread, Lock
import json
import logging
import os
import time
from dotenv import load_dotenv
from ecdsa import SigningKey, VerifyingKey
import ecdsa

load_dotenv()

class CmpECoinNetwDispatcher():

    def __init__(self, addresses):
        self.blockchainMutex = Lock()
        self.blockchain = CmpEBlockchain([])
        self.blockchain.createInitialDummyBlock(addresses)

    def run(self):
        parameters = pika.ConnectionParameters('localhost', 5672, '/', pika.PlainCredentials('user', 'password'))
        connection = pika.BlockingConnection(parameters)
        channel = connection.channel()

        channel.queue_declare(queue='blocks')

        channel.exchange_declare(exchange=os.getenv("BLOCK_EXCHANGE"), exchange_type='fanout')
        body = self.blockchain.chain[0].toJSON()
        channel.basic_publish(exchange= os.getenv("BLOCK_EXCHANGE"), routing_key='', body=body)
        print(" [g] Forwarded the genesis block to all nodes ")

        transactionThread = Thread(target=self.listenForTransactions)
        validatedBlocksThread = Thread(target=self.listenForValidatedBlocks)
        sendValidateBeacon = Thread(target = self.sendValidateBeacon)
        transactionThread.start()
        validatedBlocksThread.start()
        sendValidateBeacon.start()

    def sendTransx(selfi,transx):
        parameters = pika.ConnectionParameters('localhost', 5672, '/', pika.PlainCredentials('user', 'password'))
        connection = pika.BlockingConnection(parameters)
        channel = connection.channel()
        channel.exchange_declare(exchange=os.getenv("TRANSX_EXCHANGE"), exchange_type='fanout')
        channel.basic_publish(exchange=os.getenv("TRANSX_EXCHANGE"), routing_key='', body=transx)
        print(" [t] Forwarded the transaction to all validator blocks")
        return True

    def listenForTransactions(self):
        parameters = pika.ConnectionParameters('localhost', 5672, '/', pika.PlainCredentials('user', 'password'))
        connection = pika.BlockingConnection(parameters)
        channel = connection.channel()

        channel.queue_declare(queue='newTransx')
        #channel.exchange_declare(exchange=os.getenv("TRANSX_EXCHANGE"), exchange_type='fanout')
    
        def callback(ch, method, properties, body):
            print(" [x] Received a new transaction")
            ch.basic_ack(delivery_tag=method.delivery_tag)

            th = Thread(target = self.sendTransx, args=(body,))
            th.start()
            th.join()
            #channel.exchange_declare(exchange=os.getenv("TRANSX_EXCHANGE"), exchange_type='fanout')

            """channel.basic_publish(exchange=os.getenv("TRANSX_EXCHANGE"), routing_key='', body=body)
            print(" [x] Forwarded the transaction to all validator blocks")"""

        channel.basic_consume(queue='newTransx', on_message_callback=callback)

        print(' [*] Waiting for new transactions. To exit press CTRL+C')
        channel.start_consuming()

    def listenForValidatedBlocks(self):
        parameters = pika.ConnectionParameters('localhost', 5672, '/', pika.PlainCredentials('user', 'password'))
        connection = pika.BlockingConnection(parameters)
        channel = connection.channel()

        channel.queue_declare(queue=os.getenv("VALIDATED_TO_DISP"))

        channel.exchange_declare(exchange=os.getenv("BLOCK_EXCHANGE"), exchange_type='fanout')

        def callback(ch, method, properties, body):
            block = self.parseBlock(body)
            print(" [B] Received a validated block")
            ch.basic_ack(delivery_tag=method.delivery_tag)

            block = self.parseBlock(body)
            self.blockchainMutex.acquire()
            self.blockchain.chain.append(block)
            if self.blockchain.isChainValid():
                self.blockchainMutex.release()
                channel.basic_publish(exchange=os.getenv("BLOCK_EXCHANGE"), routing_key='', body=body)
                print(" [fb] Forwarded the validated block to all nodes " )
            else:    
                self.blockchain.chain.pop()
                print(
                    f'[ib] received an invalid block, did not add to its blockchain.')
                self.blockchainMutex.release()

        channel.basic_consume(queue=os.getenv("VALIDATED_TO_DISP"), on_message_callback=callback)

        print(' [*] Waiting for validated blocks.')
        channel.start_consuming()

    def sendValidateBeacon(self):
        parameters = pika.ConnectionParameters('localhost', 5672, '/', pika.PlainCredentials('user', 'password'))
        connection = pika.BlockingConnection(parameters)
        channel = connection.channel()

        channel.exchange_declare(exchange = os.getenv("VALIDATION_BEACON"), exchange_type='fanout')
        queue_name = 'beacon'
        channel.queue_declare(queue=queue_name, exclusive=True)
        channel.queue_bind(exchange = os.getenv("VALIDATION_BEACON"), queue=queue_name)

        while True:
            print("[bea] Sent beacon for validated blocks.")
            time.sleep(10)
            channel.basic_publish(exchange=os.getenv("VALIDATION_BEACON"), routing_key='', body="validate")
            

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
            transaction.signature = bytes.fromhex(transactionJson["signature"]) if transactionJson["signature"] else None

            transactions.append(transaction)

        return CmpEBlock(0, transactions, blockJson["prevBlockHash"], blockJson["proofOfWork"], blockJson["timestamp"])

