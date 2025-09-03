import os
from datetime import timedelta
from sqlalchemy.pool import NullPool

class Config:
    """Base configuration settings"""

    # Get directory
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    INSTANCE_DIR = os.path.join(BASE_DIR, 'instance')

    # Set maximum session time to 3 days
    SESSION_LIFETIME = timedelta(days=3)

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Get secret key from .env file
    SECRET_KEY = os.environ.get('SECRET_KEY')

    @staticmethod
    def init_app():
        """Create instance directory if it doesn't exist"""
        if not os.path.exists(Config.INSTANCE_DIR):
            os.makedirs(Config.INSTANCE_DIR)
        return True

class DevelopmentConfig(Config):
    """Development configuration settings"""

    DEBUG = True    
    DB_NAME = 'seedlings.db'
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{os.path.join(Config.INSTANCE_DIR, DB_NAME)}'

    CORS_ORIGINS = [
        'http://loacalhost:5000',
        'http://127.0.0.1:5000'
    ]

class ProductionConfig(Config):
    """Production configuration settings"""

    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") # Get db URL for Render
    SQLALCHEMY_ENGINE_OPTIONS = {
        "poolclass":NullPool
    }
    CORS_ORIGINS = ['seedlings-5fgm.onrender.com']

# Dictionary of configurations
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
