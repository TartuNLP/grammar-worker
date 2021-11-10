import json
import logging
from sys import getsizeof
from time import time, sleep

import pika
import pika.exceptions

from .dataclasses import Response, Request
from .gec import GEC

LOGGER = logging.getLogger("gec_worker")


class MQConsumer:
    def __init__(self, gec: GEC,
                 connection_parameters: pika.connection.ConnectionParameters,
                 exchange_name: str,
                 routing_key: str):
        """
        Initializes a RabbitMQ consumer class that listens for requests for a specific worker and responds to
        them.

        :param gec: A GEC instance to be used.
        :param connection_parameters: RabbitMQ connection_parameters parameters.
        :param exchange_name: RabbitMQ exchange name.
        :param routing_key: RabbitMQ routing key.
        """
        self.gec = gec

        self.exchange_name = exchange_name
        self.routing_key = routing_key
        self.connection_parameters = connection_parameters
        self.channel = None

    def start(self):
        """
        Connect to RabbitMQ and start listening for requests. Automatically tries to reconnect if the connection
        is lost.
        """
        while True:
            try:
                self._connect()
                LOGGER.info('Ready to process requests.')
                self.channel.start_consuming()
            except pika.exceptions.AMQPConnectionError as e:
                LOGGER.error(e)
                LOGGER.info('Trying to reconnect in 5 seconds.')
                sleep(5)
            except KeyboardInterrupt:
                LOGGER.info('Interrupted by user. Exiting...')
                self.channel.close()
                break

    def _connect(self):
        """
        Connects to RabbitMQ, (re)declares the exchange for the service and a queue for the worker binding
        any alternative routing keys as needed.
        """
        LOGGER.info(f'Connecting to RabbitMQ server: {{host: {self.connection_parameters.host}, '
                    f'port: {self.connection_parameters.port}}}')
        connection = pika.BlockingConnection(self.connection_parameters)
        self.channel = connection.channel()
        self.channel.queue_declare(queue=self.routing_key)
        self.channel.exchange_declare(exchange=self.exchange_name, exchange_type='direct')

        self.channel.queue_bind(exchange=self.exchange_name, queue=self.routing_key, routing_key=self.routing_key)

        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(queue=self.routing_key, on_message_callback=self._on_request)

    @staticmethod
    def _respond(channel: pika.adapters.blocking_connection.BlockingChannel, method: pika.spec.Basic.Deliver,
                 properties: pika.BasicProperties, body: bytes):
        """
        Publish the response to the callback queue and acknowledge the original queue item.
        """
        channel.basic_publish(exchange='',
                              routing_key=properties.reply_to,
                              properties=pika.BasicProperties(
                                  correlation_id=properties.correlation_id,
                                  content_type='application/json'),
                              body=body)
        channel.basic_ack(delivery_tag=method.delivery_tag)

    def _on_request(self, channel: pika.adapters.blocking_connection.BlockingChannel, method: pika.spec.Basic.Deliver,
                    properties: pika.BasicProperties, body: bytes):
        """
        Pass the request to the GEC and return its response.
        """
        t1 = time()
        LOGGER.info(f"Received request: {{id: {properties.correlation_id}, size: {getsizeof(body)} bytes}}")
        try:
            request = json.loads(body)
            request = Request(**request)
            response = self.gec.process_request(request)
        except Exception as e:
            LOGGER.exception(f'Unexpected error: {e}')
            response = Response(status_code=500, status="Unknown internal error.")

        response_size = getsizeof(response)

        self._respond(channel, method, properties, response.encode())
        t2 = time()

        LOGGER.info(f"Request processed: {{id: {properties.correlation_id}, duration: {round(t2 - t1, 3)} s, "
                    f"size: {response_size} bytes}}")
