import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    COSMOS_DB_URL = os.getenv('COSMOS_DB_URL')
    COSMOS_DB_KEY = os.getenv('COSMOS_DB_KEY')
    COSMOS_DB_DATABASE = os.getenv('COSMOS_DB_DATABASE')
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

config = Config()
print("Configuration loaded successfully.")