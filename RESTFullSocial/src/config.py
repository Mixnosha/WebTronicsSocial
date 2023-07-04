from dotenv import load_dotenv
import os

load_dotenv()

DB_HOST = os.environ.get("DB_HOST")
DB_PASS = os.environ.get("DB_PASS")
DB_USER = os.environ.get("DB_USER")
DB_NAME = os.environ.get("DB_NAME")
DB_PORT = os.environ.get("DB_PORT")
SECRET = str(os.environ.get("SECRET"))
RESET_SECRET = str(os.environ.get("RESET_SECRET"))
VERIFICATION_SECRET = str(os.environ.get("VERIFICATION_SECRET"))
HUNTER_KEY = os.environ.get("HUNTER_KEY")
