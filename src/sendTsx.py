import pika
import json
Publics = {0:'093bd529134dfb8d23f790b0ee86c5ddceb5799701331c46ea767daab1a4b09b4478c1b05e34f7e885345e83c0222fe0883ca6ab2621447c34472d0416c0eb7c', 1:'280ce949f4b465987b8e3aa69ba4bab7dbc0f8792f237fb097322d4d8174f875e37490e81dd864499ae46cf869e338b3b35839d7946575cb8417b935dceefba7', 2:'8be6ff238a7989d72d543bdf07df7132604fb95e7842f81e8ca140cdc8bbe247054ec61caa6e88075c5a200d0fd1b7394c3cad0dd2c1d062babdf01ec0d718da'}
parameters = pika.ConnectionParameters('localhost', 5672, '/', pika.PlainCredentials('user', 'password'))
while True:
    To = input("Send To? ")
    inpF = input("transaction from? ")
    inpT = input("transaction to? ")
    amount = input("transaction amount? ")

    queue_name = 'transactiona' + Publics.get(int(To), 0)
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()
    body = {"fromAddress" : Publics.get(int(inpF), 0),
        "toAddress": Publics.get(int(inpT), 0),
        "amount": float(amount)
    }
    channel.queue_declare(queue=queue_name)

    channel.basic_publish(exchange='', routing_key=queue_name, body=json.dumps(body))

    print("TSX SENT")

    
