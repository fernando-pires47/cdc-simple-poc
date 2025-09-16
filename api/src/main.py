
from fastapi import FastAPI, Response
from pymongo import MongoClient
from bson import ObjectId
import os
import json
import redis

app = FastAPI()

# Connect to MongoDB
client = MongoClient(os.environ.get("MONGO_URI", "mongodb://mongo:27017/"))
db = client.cdc_data

# Connect to Redis
redis_host = os.environ.get("REDIS_HOST", "redis")
r = redis.Redis(host=redis_host, port=6379, db=0, decode_responses=True)


class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)

@app.get("/users")
def read_users():
    users = list(db.users.find())
    return Response(content=json.dumps({"users": users}, cls=JSONEncoder), media_type="application/json")

@app.get("/products")
def read_products():
    products = list(db.products.find())
    return Response(content=json.dumps({"products": products}, cls=JSONEncoder), media_type="application/json")

@app.get("/check-redis/{key}")
def check_redis(key: str):
    value = r.get(key)
    if value:
        return {"key": key, "value": value}
    else:
        return {"key": key, "found": False}

@app.get("/check-redis/user/{user_id}")
def check_user(user_id: int):
    key = f"cdc.public.users:{user_id}"
    value = r.get(key)
    if value:
        return {"key": key, "value": value, "found": True}
    else:
        return {"key": key, "found": False}

@app.get("/check-redis/product/{product_id}")
def check_product(product_id: int):
    key = f"cdc.public.products:{product_id}"
    value = r.get(key)
    if value:
        return {"key": key, "value": value, "found": True}
    else:
        return {"key": key, "found": False}
