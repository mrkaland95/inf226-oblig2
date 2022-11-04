import pathlib
from .database import init_db
from .utils import get_secret_key
from flask import Flask
from flask_login import LoginManager

"""
File that works as the entry point for the app.
"""

# This is defined here, as per the documentation you can instantiate it once
# and then bind it to the various blueprints.
secret_key_path = pathlib.Path('.secret_key')
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
# login_manager.login_message_category = 'info'


def create_app():
    """
    Initializes the actual app.
    :return:
    """
    # Set up app
    app = Flask(__name__)
    # Generates a secret key if it does not exist, and puts it in the .secret_key file.
    # Alternatively if it does exist, reads from it.
    app.secret_key = get_secret_key(secret_key_path)
    # Inits the login manager and db.
    login_manager.init_app(app)
    init_db()

    # These are imported here to get past circular imports.
    from .routes import routes
    from .auth import auth

    app.register_blueprint(auth)
    app.register_blueprint(routes)

    return app


def main():
    create_app()


if __name__ == '__main__':
    main()










