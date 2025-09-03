import eventlet
eventlet.monkey_patch()

from flask import Flask
from flask_login import LoginManager
from models.base_content import base_content
from flask_socketio import SocketIO
import os
from config import config
from dotenv import load_dotenv
from models.database import db

# Initialise Socket.IO
socketio = SocketIO()

# Load .env file and its variables
load_dotenv()

def create_app(config_name=os.environ.get('FLASK_ENV')):
    """Start application"""
    app = Flask(__name__)
    app.config.from_object(config[config_name]) # Get configuration type
    config[config_name].init_app()

    # Initialise extensions
    db.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.init_app(app)

    # Initialise Socket.IO with app
    # Limit allowed origins for security
    socketio.init_app(app, cors_allowed_origins=app.config['CORS_ORIGINS'])

    # Initialise Socket.IO events
    from sockets.events import init_socket_events
    init_socket_events(socketio)

    from models.user import User

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(id)

    # Register blueprints
    from routes.auth import auth
    from routes.views import views
    from routes.rooms import rooms
    from routes.game import game
    
    app.register_blueprint(auth, url_prefix='/')
    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(rooms, url_prefix='/')
    app.register_blueprint(game, url_prefix='/')

    # Create database if one doesnt exist
    with app.app_context():
        db.create_all()
        # Add base data
        base_content()
        print(f'Database ready at: {app.config["SQLALCHEMY_DATABASE_URI"]}')

    return app

if __name__ == '__main__':
    app = create_app()
    socketio.run(app, debug=app.config['DEBUG']) # Set debug type