from pymongo import MongoClient
client = MongoClient()
client.drop_database('my-collaborative-app')
print('my-collaborative-app database deleted with class')