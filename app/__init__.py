from flask import Flask
from pymessenger.bot import Bot
from pathlib import Path
from dotenv import load_dotenv
import os
from flask_sqlalchemy import SQLAlchemy

env_path = Path('..') / '.env'
load_dotenv(dotenv_path=env_path)

app = Flask(__name__)

# Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///./database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')
VERIFY_TOKEN = os.getenv('VERIFY_TOKEN')
bot = Bot(ACCESS_TOKEN)


from app import routes
from app.commands import *