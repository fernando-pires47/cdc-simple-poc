import os
import json
import logging
from kafka import KafkaConsumer
from pymongo import MongoClient

logging.basicConfig(level=logging.INFO)

# Kafka Configuration
KAFKA_BROKER = os.environ.get("KAFKA_BROKER", "localhost:29092")
USER_TOPIC = 'cdc.public.users'
PRODUCT_TOPIC = 'cdc.public.products'

# MongoDB Configuration
MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017/")
MONGO_DB = 'cdc_data'
USER_COLLECTION = 'users'
PRODUCT_COLLECTION = 'products'

# MongoDB Client
client = MongoClient(MONGO_URI)
db = client[MONGO_DB]
user_collection = db[USER_COLLECTION]
product_collection = db[PRODUCT_COLLECTION]

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
            collection = user_collection
        elif topic == PRODUCT_TOPIC:
            collection = product_collection
        else:
            continue

        if data and (data['payload']['op'] == 'c' or data['payload']['op'] == 'r'):
            new_record = data['payload']['after']
            collection.insert_one(new_record)
            logging.info(f"Inserted record: {new_record}")

        if data and data['payload']['op'] == 'u':
            updated_record = data['payload']['after']
            collection.update_one({'id': updated_record['id']}, {'$set': updated_record})
            logging.info(f"Updated record: {updated_record}")

        if data and data['payload']['op'] == 'd':
            deleted_record = data['payload']['before']
            collection.delete_one({'id': deleted_record['id']})
            logging.info(f"Deleted record: {deleted_record}")

if __name__ == "__main__":
    kafka_consumer()
