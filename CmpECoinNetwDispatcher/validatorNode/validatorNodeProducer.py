#!/usr/bin/env python
import pika

connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

channel.queue_declare(queue='blocks')

channel.basic_publish(exchange='', routing_key='blocks', body='Hello World!')
print(" [x] Sent a validated block from a validator node")
connection.close()