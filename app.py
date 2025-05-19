from flask import Flask
from flask_login import LoginManager
from flask_migrate import Migrate
import os
from config import config
from dotenv import load_dotenv
from models.database import db

# Load .env file and its variables
load_dotenv()

def create_app(config_name=os.environ.get('FLASK_ENV')):
    """Start application"""
    app = Flask(__name__)
    app.config.from_object(config[config_name]) # Get configuration type
    config[config_name].init_app()

    # Initialise extentions
    db.init_app(app)
    migrate = Migrate(app, db)

    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.init_app(app)

    from models.user import User

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(id)

    # Register blueprints
    from routes.auth import auth
    from routes.views import views
    
    app.register_blueprint(auth, url_prefix='/')
    app.register_blueprint(views, url_prefix='/')

    # Create database if one doesnt exist
    with app.app_context():
        db.create_all()
        print(f'Database ready at: {app.config["SQLALCHEMY_DATABASE_URI"]}')

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=app.config['DEBUG']) # Set debug type