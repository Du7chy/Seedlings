import os
from datetime import timedelta

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

class ProductionConfig(Config):
    """Production configuration settings"""

    DEBUG = False
    # Will be replaced later for PythonAnywhere database configuration
    SQLALCHEMY_DATABASE_URI = 'PLACEHOLDER'

# Dictionary of configurations
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

