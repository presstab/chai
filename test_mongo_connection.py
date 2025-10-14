import os
from pymongo import MongoClient

# Update this connection string for your MongoDB setup
# For local: "mongodb://localhost:27017/"
# For Atlas: "mongodb+srv://username:password@cluster.mongodb.net/"

# example for Mongo Atlas
# **IMPORTANT** You must set the environment variable MONGO_KEY from your terminal if you are using Atlas
# This is something that does not persist from one terminal session to another, so remember to do it!
# For Windows Command Prompt: set MONGO_KEY=password_here
# For Windows PowerShell: $env:MONGO_KEY = "lab2mongodb"
# For Mac/Linux: export MONGO_KEY="password_here"
user = os.getenv("MONGO_USER") # replace with your username in Atlas
password = os.getenv("MONGO_PASSWORD")
srv = os.getenv("MONGO_SRV")
cluster = os.getenv("MONGO_CLUSTER")
requirements = os.getenv("MONGO_REQURIREMENTS")
# Edit the url to use the url it gives you - remember to enter username and password as is done below
connection_string = f"{srv}://{user}:{password}@{cluster}/{requirements}"
# mongodb+srv://ahezekiah_db_mongo:lab2mongodb@cluster0.ew8zh8g.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0


# example for Local mongodb
# connection_string = "mongodb://localhost:27017/"

try:
    client = MongoClient(connection_string)
    # Test the connection
    client.admin.command('ping')
    print("Successfully connected to MongoDB!")
    client.close()
except Exception as e:
    print(f"Failed to connect: {e}")