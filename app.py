from flask import Flask
import os
from config import config
from dotenv import load_dotenv

# Load .env file and its variables
load_dotenv()

def init_app(config_name=os.environ.get('FLASK_ENV')):
    """Start application"""
    app = Flask(__name__)
    app.config.from_object(config[config_name]) # Get configuration type
    config[config_name].create_app()

if __name__ == '__main__':
    app = init_app()
    app.run(debug=app.config['DEBUG']) # Set debug type