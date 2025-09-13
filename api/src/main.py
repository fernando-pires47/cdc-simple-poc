
from fastapi import FastAPI, Response
from pymongo import MongoClient
from bson import ObjectId
import os
import json

app = FastAPI()

# Connect to MongoDB
client = MongoClient(os.environ.get("MONGO_URI", "mongodb://mongo:27017/"))
db = client.cdc_data

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
