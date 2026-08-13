import time

import pymongo
from pymongo import MongoClient
from config.config import mongodb_config

mongo_client = None

def get_mongo_client():
    global mongo_client
    if not mongo_client:
        mongo_client = MongoClient(mongodb_config.mongo_url)
    return mongo_client

collection =None
def get_mongo_collection():
    global collection
    mongo_client = get_mongo_client()
    db = mongo_client[mongodb_config.mongo_db_name]
    if collection is None:
        collection = db['the_fucking_history']
        collection.create_index([('_id', 1),('ts',-1),('session_id',1)])
    return collection

def get_recent_history_list(session_id,limit=10):
    collection = get_mongo_collection()
    res = collection.find({'session_id':session_id}).sort('ts',-1).limit(limit)
    return res

def add_or_update_history(session_id,role,text,rewritten_query=None,item_names=None,ts=None,message_id=None,_id=None):
    collection = get_mongo_collection()
    if _id:
        data = {
            '_id': _id,
            'session_id': session_id,
            'role': role,
            'text': text,
            'rewritten_query': rewritten_query,
            'item_names': item_names,
            'ts': ts or time.time()
        }
        collection.update_one({'_id': _id}, {'$set': data})
        return _id
    else:
        data = {
            'session_id': session_id,
            'role': role,
            'text': text,
            'rewritten_query': rewritten_query,
            'item_names': item_names,
            'ts': ts or time.time()
        }
        res = collection.insert_one(data)
        print(res.inserted_id)
        return res.inserted_id

def clear_history(session_id):
    collection = get_mongo_collection()
    collection.delete_many({'session_id': session_id})


#  这他妈是回填
def update_item_names_and_query(ids, item_names=None, rewritten_query=None):
    collection = get_mongo_collection()
    data = {
        'rewritten_query': rewritten_query,
        'item_names': item_names
    }
    collection.update_many({'_id': {'$in':ids}}, {'$set': data})


if __name__ == '__main__':
    session_id = "test_001"
    res = add_or_update_history(session_id, "user", "咨询下烫金机。")

