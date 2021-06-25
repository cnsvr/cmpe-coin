#!/usr/bin/env python
import pika, threading

connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

channel.queue_declare(queue='newTransx')

channel.basic_publish(exchange='', routing_key='newTransx', body='Hello World!')
print(" [x] Sent a transaction from a simple node")
connection.close()