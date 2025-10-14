import os
from pymongo import MongoClient

# Update this connection string for your MongoDB setup
# For local: "mongodb://localhost:27017/"
# For Atlas: "mongodb+srv://username:password@cluster.mongodb.net/"

# example for Mongo Atlas
# **IMPORTANT** You must set the environment variable MONGO_KEY from your terminal if you are using Atlas
# This is something that does not persist from one terminal session to another, so remember to do it!
# For Windows Command Prompt: set MONGO_KEY=password_here
# For Windows PowerShell: $env:MONGO_KEY = "password_here"
# For Mac/Linux: export MONGO_KEY="password_here"
user = "tom" # replace with your username in Atlas
password = os.getenv("MONGO_KEY")
# Edit the url to use the url it gives you - remember to enter username and password as is done below
connection_string = f"mongodb+srv://{user}:{password}@cluster0.3walskx.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

# example for Local mongodb
connection_string = "mongodb://localhost:27017/"

try:
    client = MongoClient(connection_string)
    # Test the connection
    client.admin.command('ping')
    print("Successfully connected to MongoDB!")
    client.close()
except Exception as e:
    print(f"Failed to connect: {e}")