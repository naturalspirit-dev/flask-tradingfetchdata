# Import Libraries 
from flask import Flask
import os
from models.index import db
from dotenv import load_dotenv
load_dotenv()

# Define app.
app = Flask(__name__)

# Database connection configuration
database_name=os.getenv("DATABASE_NAME")
username=os.getenv("USER_NAME")
password=os.getenv("PASSWORD")
hostname=os.getenv("HOSTNAME")
port=os.getenv("PORT")
print(f'postgresql://{username}:{password}@{hostname}:{port}/{database_name}')

app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{username}:{password}@{hostname}:{port}/{database_name}'
# app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://postgres:123123123@localhost:5432/ITD'

def init_db():
    with app.app_context():
            db.init_app(app)
            db.create_all()

init_db()


# Import the __init__.py from modules which had imported all files from the folder.
import modules
