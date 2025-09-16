
from fastapi import FastAPI, Response
from elasticsearch import Elasticsearch
import os
import json
import redis

app = FastAPI()

# Connect to Elasticsearch
es_host = os.environ.get("ELASTICSEARCH_HOST", "elasticsearch")
es = Elasticsearch([f"http://{es_host}:9200"])

# Connect to Redis
redis_host = os.environ.get("REDIS_HOST", "redis")
r = redis.Redis(host=redis_host, port=6379, db=0)

@app.get("/users")
def read_users():
    try:
        res = es.search(index="cdc.public.users", body={"query": {"match_all": {}}})
        users = [hit["_source"] for hit in res["hits"]["hits"]]
        return Response(content=json.dumps({"users": users}), media_type="application/json")
    except Exception as e:
        return Response(content=json.dumps({"error": str(e)}), media_type="application/json", status_code=500)

@app.get("/products")
def read_products():
    try:
        res = es.search(index="cdc.public.products", body={"query": {"match_all": {}}})
        products = [hit["_source"] for hit in res["hits"]["hits"]]
        return Response(content=json.dumps({"products": products}), media_type="application/json")
    except Exception as e:
        return Response(content=json.dumps({"error": str(e)}), media_type="application/json", status_code=500)

@app.get("/check-redis/user/{user_id}")
def check_user(user_id: int):
    key = f"user:{user_id}"
    value = r.hgetall(key)
    return {"key": key, "value": value}

@app.get("/check-redis/product/{product_id}")
def check_product(product_id: int):
    key = f"product:{product_id}"
    value = r.hgetall(key)
    return {"key": key, "value": value}
