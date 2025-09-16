import os
import json
import logging
from kafka import KafkaConsumer
import redis

logging.basicConfig(level=logging.INFO)

# Kafka Configuration
KAFKA_BROKER = os.environ.get("KAFKA_BROKER", "localhost:29092")
USER_TOPIC = 'cdc.public.users'
PRODUCT_TOPIC = 'cdc.public.products'

# Redis Configuration
REDIS_HOST = os.environ.get("REDIS_HOST", "localhost")
REDIS_PORT = 6379

# Redis Client
redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0)

def kafka_consumer():
    logging.info("Connecting to Kafka broker at %s", KAFKA_BROKER)
    try:
        consumer = KafkaConsumer(
            USER_TOPIC,
            PRODUCT_TOPIC,
            bootstrap_servers=KAFKA_BROKER,
            auto_offset_reset='earliest',
            value_deserializer=lambda m: json.loads(m.decode('utf-8')) if m is not None else None
        )
        logging.info("Consumer started...")
    except Exception as e:
        logging.error("Could not connect to Kafka: %s", e)
        return

    for message in consumer:
        logging.info(f"Received message: {message}")
        data = message.value
        topic = message.topic
        logging.info(f"Received message from topic {topic}: {data}")

        if topic == USER_TOPIC:
            redis_key_prefix = "user"
        elif topic == PRODUCT_TOPIC:
            redis_key_prefix = "product"
        else:
            continue

        if data and (data['payload']['op'] == 'c' or data['payload']['op'] == 'r'):
            new_record = data['payload']['after']
            logging.info(f"New record: {new_record}")
            redis_key = f"{redis_key_prefix}:{new_record['id']}"
            redis_client.hmset(redis_key, {k: str(v).encode('utf-8') for k, v in new_record.items()})
            logging.info(f"Cached record in Redis: {redis_key}")

        if data and data['payload']['op'] == 'u':
            updated_record = data['payload']['after']
            logging.info(f"Updated record: {updated_record}")
            redis_key = f"{redis_key_prefix}:{updated_record['id']}"
            redis_client.hmset(redis_key, updated_record)
            logging.info(f"Updated cache in Redis: {redis_key}")

        if data and data['payload']['op'] == 'd':
            deleted_record = data['payload']['before']
            logging.info(f"Deleted record: {deleted_record}")
            redis_key = f"{redis_key_prefix}:{deleted_record['id']}"
            redis_client.delete(redis_key)
            logging.info(f"Deleted cache in Redis: {redis_key}")

if __name__ == "__main__":
    kafka_consumer()