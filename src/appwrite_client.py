from appwrite.client import Client
from appwrite.services.databases import Databases
from appwrite.services.tables_db import TablesDB
import config

client = Client()
client.set_endpoint(config.APPWRITE_ENDPOINT)
client.set_project(config.APPWRITE_PROJECT)
client.set_key(config.APPWRITE_API_KEY)

db = Databases(client)
tables = TablesDB(client)

def get_users():
    return db.list_documents(
        database_id=config.APPWRITE_DB,
        collection_id=config.APPWRITE_COLLECTION
    )['documents']
