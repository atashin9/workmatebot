import os
from dotenv import load_dotenv

load_dotenv()

database_name = os.environ.get('database_name')

database_config = {
    'user': os.environ.get('database_user'),
    'password': os.environ.get('database_password'),
    'host': os.environ.get('database_host')
}