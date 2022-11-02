import os
import pathlib
import secrets
from http import HTTPStatus

import bcrypt
from flask import Flask, abort, request, send_from_directory, make_response, render_template
from werkzeug.datastructures import WWWAuthenticate
from login_form import LoginForm
from json import dumps, loads
from base64 import b64decode
from apsw import Error
from pygments import highlight
from pygments.lexers import SqlLexer
from pygments.formatters import HtmlFormatter
from pygments.filters import NameHighlightFilter, KeywordCaseFilter
from pygments import token
from threading import local
from markupsafe import escape
import flask
import sys
import apsw


inject = "'; insert into messages (sender,message) values ('foo', 'bar');select '"
cssData = HtmlFormatter(nowrap=True).get_style_defs('.highlight')

# Set up app
app = Flask(__name__)
# The secret key enables storing encrypted session data in a cookie (make a secure random key for this!)
app.secret_key = 'mY s3kritz'
DATABASE_NAME = './tiny.db'

# Add a login manager to the app
import flask_login
from flask_login import login_required, login_user


login_manager = flask_login.LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


users = {'alice': {'password': 'password123', 'token': 'tiktok'},
         'bob': {'password': 'bananas'}
         }


# Class to store user info
# UserMixin provides us with an `id` field and the necessary
# methods (`is_authenticated`, `is_active`, `is_anonymous` and `get_id()`)
class User(flask_login.UserMixin):
    pass


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


# This method is called whenever the login manager needs to get
# the User object for a given user id
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


@app.route('/favicon.ico')
def favicon_ico():
    return send_from_directory(app.root_path, 'favicon.ico', mimetype='image/vnd.microsoft.icon')


@app.route('/favicon.png')
def favicon_png():
    return send_from_directory(app.root_path, 'favicon.png', mimetype='image/png')


@app.route('/')
@app.route('/index.html')
@login_required
def index_html():
    return send_from_directory(app.root_path,
                               'index.html', mimetype='text/html')


def add_new_user_to_database(user_to_add, password_to_add):
    """
    Adds a specified user to the database

    :param user_to_add:
    :param password_to_add:
    :return:
    """
    try:
        query = 'INSERT INTO users (user_name, password) VALUES (?, ?)', (user_to_add, password_to_add)
        connection = apsw.Connection(DATABASE_NAME)
        cursor = connection.cursor()
        cursor.execute(query)

    except apsw.Error as e:
        print(e)
        sys.exit(1)


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


def validate_login(username, password):
    """

    :param username: The user that is to be checked for in the database.
    :param password: The password that is to be checked.
    :return: Returns a bool if the login was valid or not.
    """
    result = False
    try:
        query = 'SELECT * FROM users WHERE user_name = (?)'
        connection = apsw.Connection(DATABASE_NAME)
        cursor = connection.cursor()
        cursor.execute(query, (username,))
        fetch_result = cursor.fetchone()
        if fetch_result:
            password_in_db = fetch_result[2]
            result = True if password_in_db == password else False
            # result = check_password(password, password_in_db)
            print(f'{password_in_db = }')
            print(f'{result = }')
    except apsw.Error as err:
        print(err)

    return result


@app.route('/register')
def register():
    print()

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    redirect_on_failure = render_template('./login.html', form=form)
    if form.is_submitted():
        print(f'Received form: {"invalid" if not form.validate() else "valid"} {form.form_errors} {form.errors}')
        print(request.form)

    if not form.validate_on_submit():
        return redirect_on_failure

    username = form.username.data
    password = form.password.data

    valid_login = validate_login(username, password)

    if not valid_login:
        return redirect_on_failure

    user = user_loader(username)

    # automatically sets logged in session cookie
    login_user(user)

    flask.flash('Logged in successfully.')

    next = flask.request.args.get('next')

    # is_safe_url should check if the url is safe for redirects.
    # See http://flask.pocoo.org/snippets/62/ for an example.
    if False and not is_safe_url(next):
        return flask.abort(400)

    return flask.redirect(next or flask.url_for('index'))



@app.get('/search')
def search():
    # FIXME SQL injection possible here
    query = request.args.get('q') or request.form.get('q') or '*'
    stmt = f"SELECT * FROM messages WHERE message GLOB '{query}'"
    result = f"Query: {pygmentize(stmt)}\n"
    try:
        connection = apsw.Connection(DATABASE_NAME)
        c = connection.execute(stmt)
        rows = c.fetchall()
        result = result + 'Result:\n'
        for row in rows:
            result = f'{result}    {dumps(row)}\n'
        c.close()
        return result
    except apsw.Error as e:
        return f'{result}ERROR: {e}', 500


@app.route('/send', methods=['POST', 'GET'])
def send():
    try:
        connection = apsw.Connection(DATABASE_NAME)
        cursor = connection.cursor()
        sender = request.args.get('sender') or request.form.get('sender')
        message = request.args.get('message') or request.args.get('message')
        if not sender or not message:
            return f'ERROR: missing sender or message'
        stmt = f"INSERT INTO messages (sender, message) values ('{sender}', '{message}');"
        result = f"Query: {pygmentize(stmt)}\n"
        cursor.execute(stmt)
        return f'{result}ok'
    except apsw.Error as e:
        return f'{result}ERROR: {e}'


@app.get('/announcements')
def announcements():
    query = f"SELECT author,text FROM announcements;"
    try:
        connection = apsw.Connection(DATABASE_NAME)
        cursor = connection.cursor()
        c = cursor.execute(query)
        anns = []
        for row in c:
            anns.append({'sender': escape(row[0]), 'message': escape(row[1])})
        return {'data': anns}
    except Error as e:
        return {'error': f'{e}'}


@app.get('/coffee/')
def nocoffee():
    abort(418)


@app.route('/coffee/', methods=['POST', 'PUT'])
def gotcoffee():
    return "Thanks!"


@app.get('/highlight.css')
def highlightStyle():
    resp = make_response(cssData)
    resp.content_type = 'text/css'
    return resp



try:
    connection = apsw.Connection(DATABASE_NAME)
    cursor = connection.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS messages (
        id integer PRIMARY KEY, 
        sender TEXT NOT NULL,
        message TEXT NOT NULL);''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS announcements (
        id integer PRIMARY KEY, 
        author TEXT NOT NULL,
        text TEXT NOT NULL);''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
        id integer PRIMARY KEY,
        user_name TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL);''')
except apsw.Error as e:
    print(e)
    sys.exit(1)


def init_database():
    """
    Initialises the database if it doesen't exist and adds fields.

    :return:
    """
    try:
        connection = apsw.Connection(DATABASE_NAME)
        cursor = connection.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS messages (
            id integer PRIMARY KEY, 
            sender TEXT NOT NULL,
            message TEXT NOT NULL);''')

        cursor.execute('''CREATE TABLE IF NOT EXISTS announcements (
            id integer PRIMARY KEY, 
            author TEXT NOT NULL,
            text TEXT NOT NULL);''')

        cursor.execute('''CREATE TABLE IF NOT EXISTS users (
            id integer PRIMARY KEY,
            user_name TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL);''')


    except apsw.Error as e:
        print(e)
        sys.exit(1)


# def main():
#     init_database()
#
#
# main()

