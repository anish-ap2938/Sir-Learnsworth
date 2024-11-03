import os
from azure.cosmos import CosmosClient, PartitionKey
from dotenv import load_dotenv
from app.config.config import config

# Load environment variables
load_dotenv()

# Retrieve Cosmos DB credentials from environment variables
cosmos_db_url = config.COSMOS_DB_URL
cosmos_db_key = config.COSMOS_DB_KEY

# Verify that credentials are loaded
if not cosmos_db_url or not cosmos_db_key:
    raise ValueError("Missing Cosmos DB credentials. Please check your .env file.")

# Initialize Cosmos DB client
client = CosmosClient(cosmos_db_url, credential=cosmos_db_key)

# Connect to the existing "learnsworth" database
database = client.get_database_client("learnsworth")

# Create or connect to containers
users_container = database.create_container_if_not_exists(
    id="users",
    partition_key=PartitionKey(path="/id"),
    offer_throughput=400
)

conversations_container = database.create_container_if_not_exists(
    id="conversations",
    partition_key=PartitionKey(path="/id"),
    offer_throughput=400
)
