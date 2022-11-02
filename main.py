import os
import secrets
from pathlib import Path
import flask
from flask import Flask, abort, request, send_from_directory, make_response, render_template
from werkzeug.datastructures import WWWAuthenticate
from auth import LoginForm
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
import database
import auth

# Add a login manager to the app
import flask_login
from flask_login import login_required, login_user


DATABASE_NAME = './tiny.db'

tls = local()
inject = "'; insert into messages (sender,message) values ('foo', 'bar');select '"
cssData = HtmlFormatter(nowrap=True).get_style_defs('.highlight')
conn = None

# Set up app
app = Flask(__name__)
# The secret key enables storing encrypted session data in a cookie (make a secure random key for this!)
SECRET_FILE_PATH = Path(".flask_secret")




if not os.path.exists(SECRET_FILE_PATH):
    # If the secret file does not exist, generate a new one,
    # store it in the flask object and write to file
    # Generates a 256 bit long secret key.
    with SECRET_FILE_PATH.open("w") as secret_file:
        app.secret_key = secrets.token_hex(32)
        secret_file.write(app.secret_key)
else:
    with SECRET_FILE_PATH.open("r") as secret_file:
        app.secret_key = secret_file.read()



users = {'alice': {'password': 'password123', 'token': 'tiktok'},
         'bob': {'password': 'bananas'}
         }


# Class to store user info
# UserMixin provides us with an `id` field and the necessary
# methods (`is_authenticated`, `is_active`, `is_anonymous` and `get_id()`)
class User(flask_login.UserMixin):
    pass


# This method is called to get a User object based on a request,
# for example, if using an api key or authentication token rather
# than getting the user name the standard way (from the session cookie)



def pygmentize(text):
    if not hasattr(tls, 'formatter'):
        tls.formatter = HtmlFormatter(nowrap=True)
    if not hasattr(tls, 'lexer'):
        tls.lexer = SqlLexer()
        tls.lexer.add_filter(NameHighlightFilter(names=['GLOB'], tokentype=token.Keyword))
        tls.lexer.add_filter(NameHighlightFilter(names=['text'], tokentype=token.Name))
        tls.lexer.add_filter(KeywordCaseFilter(case='upper'))
    return f'<span class="highlight">{highlight(text, tls.lexer, tls.formatter)}</span>'


@app.route('/favicon.ico')
def favicon_ico():
    return send_from_directory(app.root_path, 'resources/favicon.ico', mimetype='image/vnd.microsoft.icon')


@app.route('/favicon.png')
def favicon_png():
    return send_from_directory(app.root_path, 'resources/favicon.png', mimetype='image/png')


@app.route('/')
@app.route('/index.html')
@login_required
def index_html():
    return send_from_directory(app.root_path, 'index.html', mimetype='text/html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.is_submitted():
        print(f'Received form: {"invalid" if not form.validate() else "valid"} {form.form_errors} {form.errors}')
        print(request.form)
    if form.validate_on_submit():
        # TODO: we must check the username and password
        username = form.username.data
        password = form.password.data
        u = users.get(username)
        if u:  # and check_password(u.password, password):
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
    return render_template('./login.html', form=form)


@app.get('/search')
def search():
    query = request.args.get('q') or request.form.get('q') or '*'
    stmt = f"SELECT * FROM messages WHERE message GLOB '{query}'"
    result = f"Query: {pygmentize(stmt)}\n"
    try:
        c = conn.execute(stmt)
        rows = c.fetchall()
        result = result + 'Result:\n'
        for row in rows:
            result = f'{result}    {dumps(row)}\n'
        c.close()
        return result
    except Error as e:
        return (f'{result}ERROR: {e}', 500)


@app.route('/send', methods=['POST', 'GET'])
def send():
    try:
        sender = request.args.get('sender') or request.form.get('sender')
        message = request.args.get('message') or request.args.get('message')
        if not sender or not message:
            return f'ERROR: missing sender or message'
        stmt = f"INSERT INTO messages (sender, message) values ('{sender}', '{message}');"
        result = f"Query: {pygmentize(stmt)}\n"
        conn.execute(stmt)
        return f'{result}ok'
    except Error as e:
        return f'{result}ERROR: {e}'


@app.get('/announcements')
def announcements():
    try:
        stmt = f"SELECT author,text FROM announcements;"
        c = conn.execute(stmt)
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


def main():
    database.init_database()


if __name__ == '__main__':
    main()

