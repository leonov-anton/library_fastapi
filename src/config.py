from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.environ.get('DATABASE_URL')
TEST_DATABASE_URL = os.environ.get('TEST_DATABASE_URL')
JWT_SECRET = os.environ.get('JWT_SECRET')
JWY_ALGORITHM = os.environ.get('JWY_ALGORITHM')
