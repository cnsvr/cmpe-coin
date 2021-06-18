#!/usr/bin/env python
import pika, sys, os

try:
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()

    channel.exchange_declare(exchange='transxToBeValidated', exchange_type='fanout')

    channel.exchange_declare(exchange='validationBeacons', exchange_type='fanout')

    result = channel.queue_declare(queue='', exclusive=True)
    queue_name = result.method.queue

    channel.queue_bind(exchange='transxToBeValidated', queue=queue_name)

    print(' [*] Waiting for transactions. To exit press CTRL+C')

    def callback(ch, method, properties, body):
        print(" [x] %r a new transaction is received by validator node" % body)

    channel.basic_consume(
        queue=queue_name, on_message_callback=callback)

    channel.start_consuming()

except KeyboardInterrupt:
    print('Interrupted')
    try:
        sys.exit(0)
    except SystemExit:
        os._exit(0)