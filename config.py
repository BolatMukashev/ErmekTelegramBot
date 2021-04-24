import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
ADMINS_ID = [int(el) for el in os.getenv('ADMINS_ID').split(',')]

TEST_TABLE = os.getenv('test_table_id')
EMPLOYEES_LIST = os.getenv('employees_id')
SHOPS = os.getenv('shops_id')
PRODUCTS = os.getenv('products_id')
CREDENTIALS_FILE_NAME = os.getenv('credentials_file_name')
REQUESTS = os.getenv('requests_id')
