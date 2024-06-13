import os
from mongoengine import connect

def connect_to_mongodb():
    try:
        username = os.environ.get("USERNAME") or "username"
        password = os.environ.get("PASSWORD") or "password"
        database = os.environ.get("DATABASE") or "book-support-system"

        mongo_uri = f'mongodb+srv://{username}:{password}@cluster0.ibftatx.mongodb.net/{database}'
        connect(db=database, host=mongo_uri)
        print("CONNECTED TO MONGODB")
    except Exception as e:
        print("CONNECTION FAILED:", e)