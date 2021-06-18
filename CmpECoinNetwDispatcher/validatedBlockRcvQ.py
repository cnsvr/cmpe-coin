#!/usr/bin/env python
import pika, sys, os, threading

class validatedBlockRcvQ(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
            channel = connection.channel()

            channel.queue_declare(queue='blocks')

            channel.exchange_declare(exchange='validatedBlocks', exchange_type='fanout')

            def callback(ch, method, properties, body):
                print(" [x] Received a validated block, whose hash is %r" % body)
                ch.basic_ack(delivery_tag=method.delivery_tag)
                
                channel.basic_publish(exchange='validatedBlocks', routing_key='', body=body)
                print(" [x] Forwarded the validated block to all nodes %r" % body)

            channel.basic_consume(queue='blocks', on_message_callback=callback)

            print(' [*] Waiting for validated blocks. To exit press CTRL+C')
            channel.start_consuming()

        except KeyboardInterrupt:
            print('Interrupted')
            try:
                sys.exit(0)
            except SystemExit:
                os._exit(0)