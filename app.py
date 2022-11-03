import pathlib
from database import init_db
from utils import get_secret_key
from auth import auth
from routes import routes
from flask import Flask
from flask_login import LoginManager

"""
File that works as the entry point for the app.
"""

# This is defined here, as per the documentation you can instantiate it once
# and then bind it to the various blueprints.


def create_app():
    """
    Initializes the actual app.
    :return:
    """
    # Set up app
    app = Flask(__name__)
    # The secret key enables storing encrypted session data in a cookie (make a secure random key for this!)
    secret_key_path = pathlib.Path('/.secret_key')
    app.secret_key = get_secret_key(secret_key_path)
    init_db()
    app.register_blueprint(auth.auth)
    app.register_blueprint(routes.routes)
    return app


if __name__ == '__main__':
    app = create_app()
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.auth'
    login_manager.login_message_category = 'info'








