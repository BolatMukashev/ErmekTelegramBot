import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
ADMIN_ID = int(os.getenv('ADMIN_ID'))

TEST_TABLE = os.getenv('test_table_id')
EMPLOYEES_LIST = os.getenv('employees_id')
SHOPS = os.getenv('shops_id')
PRODUCTS = os.getenv('products_id')
CREDENTIALS_FILE_NAME = os.getenv('credentials_file_name')
REQUESTS = os.getenv('requests_id')
