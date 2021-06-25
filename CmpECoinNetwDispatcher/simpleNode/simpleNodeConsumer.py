#!/usr/bin/env python
import pika, sys, os

def main():
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()

    channel.exchange_declare(exchange='validatedBlocks', exchange_type='fanout')

    result = channel.queue_declare(queue='', exclusive=True)
    queue_name = result.method.queue

    channel.queue_bind(exchange='validatedBlocks', queue=queue_name)

    print(' [*] Waiting for validated blocks. To exit press CTRL+C')

    def callback(ch, method, properties, body):
        print(" [x] %r a new block is received by simple node" % body)

    channel.basic_consume(
        queue=queue_name, on_message_callback=callback)

    channel.start_consuming()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)