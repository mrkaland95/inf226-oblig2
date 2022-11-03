import os
import pathlib
import secrets
import bcrypt
import flask
import flask_login
import database
from flask import abort, render_template, Blueprint, request
from http import HTTPStatus
from flask_login import LoginManager
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from werkzeug.datastructures import WWWAuthenticate
from base64 import b64decode
from pygments import highlight
from pygments.lexers import SqlLexer
from pygments.filters import NameHighlightFilter, KeywordCaseFilter
from pygments import token
from threading import local



"""
File for handling the login side of the app.
"""

# FIXME remove this once implemented the database.
users = {'alice': {'password': 'password123', 'token': 'tiktok'},
         'bob': {'password': 'bananas'}}


auth = Blueprint('auth', __name__)




# Class to store user info
# UserMixin provides us with an `id` field and the necessary
# methods (`is_authenticated`, `is_active`, `is_anonymous` and `get_id()`)
class User(flask_login.UserMixin):
    pass


@app.route('/register')
def register():
    print()


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    redirect_on_failure = render_template('./auth/login.html', form=form)
    if form.is_submitted():
        print(f'Received form: {"invalid" if not form.validate() else "valid"} {form.form_errors} {form.errors}')
        print(request.form)

    if not form.validate_on_submit():
        return redirect_on_failure

    username = form.username.data
    password = form.password.data

    valid_login = database.validate_login(username, password)

    if not valid_login:
        return redirect_on_failure

    user = user_loader(username)

    # automatically sets logged in session cookie
    logged_user = login_user(user)

    flask.flash('Logged in successfully.')

    next = flask.request.args.get('next')

    # is_safe_url should check if the url is safe for redirects.
    # See http://flask.pocoo.org/snippets/62/ for an example.
    if False and not is_safe_url(next):
        return flask.abort(400)

    return flask.redirect(next or flask.url_for('index'))


# This method is called to get a User object based on a request,
# for example, if using an api key or authentication token rather
# than getting the user name the standard way (from the session cookie)
@auth.login_manager.request_loader
def request_loader(request):
    # Even though this HTTP header is primarily used for *authentication*
    # rather than *authorization*, it's still called "Authorization".
    auth = request.headers.get('Authorization')

    # If there is not Authorization header, do nothing, and the login
    # manager will deal with it (i.e., by redirecting to a login page)
    if not auth:
        return

    (auth_scheme, auth_params) = auth.split(maxsplit=1)
    auth_scheme = auth_scheme.casefold()
    if auth_scheme == 'basic':  # Basic auth has username:password in base64
        (uid, passwd) = b64decode(auth_params.encode(errors='ignore')).decode(errors='ignore').split(':', maxsplit=1)
        print(f'Basic auth: {uid}:{passwd}')
        u = users.get(uid)
        if u:  # and check_password(u.password, passwd):
            return user_loader(uid)
    elif auth_scheme == 'bearer':  # Bearer auth contains an access token;
        # an 'access token' is a unique string that both identifies
        # and authenticates a user, so no username is provided (unless
        # you encode it in the token – see JWT (JSON Web Token), which
        # encodes credentials and (possibly) authorization info)
        print(f'Bearer auth: {auth_params}')
        for uid in users:
            if users[uid].get('token') == auth_params:
                return user_loader(uid)
    # For other authentication schemes, see
    # https://developer.mozilla.org/en-US/docs/Web/HTTP/Authentication

    # If we failed to find a valid Authorized header or valid credentials, fail
    # with "401 Unauthorized" and a list of valid authentication schemes
    # (The presence of the Authorized header probably means we're talking to
    # a program and not a user in a browser, so we should send a proper
    # error message rather than redirect to the login page.)
    # (If an authenticated user doesn't have authorization to view a page,
    # Flask will send a "403 Forbidden" response, so think of
    # "Unauthorized" as "Unauthenticated" and "Forbidden" as "Unauthorized")
    flask.abort(HTTPStatus.UNAUTHORIZED, www_authenticate=WWWAuthenticate('Basic realm=inf226, Bearer'))


@login_manager.user_loader
def user_loader(user_id):
    # TODO 1. chance this to load a user from a database. Including hashing and salting.
    if user_id not in users:
        return

    # For a real app, we would load the User from a database or something
    user = User()
    user.id = user_id
    return user


# This method is called to get a User object based on a request,
# for example, if using an api key or authentication token rather
# than getting the user name the standard way (from the session cookie)
@login_manager.request_loader
def request_loader(request):
    # Even though this HTTP header is primarily used for *authentication*
    # rather than *authorization*, it's still called "Authorization".
    auth = request.headers.get('Authorization')

    # If there is not Authorization header, do nothing, and the login
    # manager will deal with it (i.e., by redirecting to a login page)
    if not auth:
        return

    (auth_scheme, auth_params) = auth.split(maxsplit=1)
    auth_scheme = auth_scheme.casefold()
    if auth_scheme == 'basic':  # Basic auth has username:password in base64
        (uid, passwd) = b64decode(auth_params.encode(errors='ignore')).decode(errors='ignore').split(':', maxsplit=1)
        print(f'Basic auth: {uid}:{passwd}')
        u = users.get(uid)
        if u:  # and check_password(u.password, passwd):
            return user_loader(uid)
    elif auth_scheme == 'bearer':  # Bearer auth contains an access token;
        # an 'access token' is a unique string that both identifies
        # and authenticates a user, so no username is provided (unless
        # you encode it in the token – see JWT (JSON Web Token), which
        # encodes credentials and (possibly) authorization info)
        print(f'Bearer auth: {auth_params}')
        for uid in users:
            if users[uid].get('token') == auth_params:
                return user_loader(uid)
    # For other authentication schemes, see
    # https://developer.mozilla.org/en-US/docs/Web/HTTP/Authentication

    # If we failed to find a valid Authorized header or valid credentials, fail
    # with "401 Unauthorized" and a list of valid authentication schemes
    # (The presence of the Authorized header probably means we're talking to
    # a program and not a user in a browser, so we should send a proper
    # error message rather than redirect to the login page.)
    # (If an authenticated user doesn't have authorization to view a page,
    # Flask will send a "403 Forbidden" response, so think of
    # "Unauthorized" as "Unauthenticated" and "Forbidden" as "Unauthorized")
    abort(HTTPStatus.UNAUTHORIZED, www_authenticate=WWWAuthenticate('Basic realm=inf226, Bearer'))


@login_manager.user_loader
def user_loader(user_name):
    # THIS IS ONLY CALLED IF THE USER IS ALREADY AUTHENTICATED
    found_user = None
    try:
        connection = apsw.Connection(DATABASE_NAME)
        cursor = connection.cursor()
        found_user = cursor.execute('''
        SELECT *
        FROM users
        WHERE (user_name) = (?)
        ''', (user_name,))
    except apsw.Error as err:
        print(err)

    if not found_user:
        return found_user

    # print(found_user.fetchall())
    # For a real app, we would load the User from a database or something
    e = list(cursor)
    user = User()
    # user.id = user_name
    user.id = e
    return user

class LoginForm(FlaskForm):
    username = StringField('Username')
    password = PasswordField('Password')
    submit = SubmitField('Submit')


def get_secret_key(file_path: pathlib.Path):
    if not os.path.exists(file_path):
        # If the secret file does not exist, generate a new one,
        # store it in the flask object and write to file
        # Generates a 256 bit long secret key.
        with file_path.open("w") as secret_file:
            secret_key = secrets.token_hex(32)
            secret_file.write(secret_key)
    else:
        with file_path.open("r") as secret_file:
            secret_key = secret_file.read()
    return secret_key

def create_hashed_and_salted_password(plaintext_password):
    """

    :param plaintext_password:
    :return:
    """
    # Bcrypt generates and inserts the salt into the password itself.
    return bcrypt.hashpw(plaintext_password, bcrypt.gensalt())

def check_password(plaintext_password: str | bytes, hashed_password: str | bytes) -> bool:
    """
    :param plaintext_password: The plaintext password string.
    :param hashed_password:
    :return: A bool of whether the password matched.
    """
    if isinstance(plaintext_password, str):
        plaintext_password = bytes(plaintext_password)
    if isinstance(hashed_password, str):
        plaintext_password = bytes(plaintext_password)
    return bcrypt.checkpw(plaintext_password, hashed_password)

def pygmentize(text):
    tls = local()
    if not hasattr(tls, 'formatter'):
        tls.formatter = HtmlFormatter(nowrap=True)
    if not hasattr(tls, 'lexer'):
        tls.lexer = SqlLexer()
        tls.lexer.add_filter(NameHighlightFilter(names=['GLOB'], tokentype=token.Keyword))
        tls.lexer.add_filter(NameHighlightFilter(names=['text'], tokentype=token.Name))
        tls.lexer.add_filter(KeywordCaseFilter(case='upper'))
    return f'<span class="highlight">{highlight(text, tls.lexer, tls.formatter)}</span>'
