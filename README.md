# cmpecoin-team-4


# Test
RabbitMq server
```bash
docker run -d --hostname my-rabbit -p 15672:15672 -p 5672:5672 --name rabbit-server -e RABBITMQ_DEFAULT_USER=user -e RABBITMQ_DEFAULT_PASS=password rabbitmq:3-management
```

Go to ```src``` directory and run the command below. It runs all tests.

```bash
python -m unittest
```
