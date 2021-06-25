#!/usr/bin/env python
import pika, sys, os, threading

class transxRcvQ(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        try:
            parameters = pika.ConnectionParameters('localhost', 5672, '/', pika.PlainCredentials('user', 'password'))
            connection = pika.BlockingConnection(parameters)
            channel = connection.channel()

            channel.queue_declare(queue='newTransx')

            channel.exchange_declare(exchange='transxToBeValidated', exchange_type='fanout')

            def callback(ch, method, properties, body):
                print(" [x] Received a new transaction, whose hash is %r" % body)
                ch.basic_ack(delivery_tag=method.delivery_tag)
                
                channel.basic_publish(exchange='transxToBeValidated', routing_key='', body=body)
                print(" [x] Forwarded the transaction to all validator blocks, %r" % body)

            channel.basic_consume(queue='newTransx', on_message_callback=callback)

            print(' [*] Waiting for new transactions. To exit press CTRL+C')
            channel.start_consuming()

        except KeyboardInterrupt:
            print('Interrupted')
            try:
                sys.exit(0)
            except SystemExit:
                os._exit(0)