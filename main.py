import os
import secrets
from pathlib import Path
from flask import Flask, abort, request, send_from_directory, make_response, render_template
from json import dumps, loads
from apsw import Error
from pygments import highlight
from pygments.lexers import SqlLexer
from pygments.formatters import HtmlFormatter
from pygments.filters import NameHighlightFilter, KeywordCaseFilter
from pygments import token
from threading import local
from markupsafe import escape

import auth
import database

# Add a login manager to the app
import flask_login
from flask_login import login_required, login_user


DATABASE_NAME = './tiny.db'

tls = local()
# inject = "'; insert into messages (sender,message) values ('foo', 'bar');select '"
cssData = HtmlFormatter(nowrap=True).get_style_defs('.highlight')
conn = None

# Set up app
app = Flask(__name__, template_folder='./templates/')

login_manager = flask_login.LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# The secret key enables storing encrypted session data in a cookie (make a secure random key for this!)
SECRET_FILE_PATH = Path(".flask_secret")

app.secret_key = auth.get_secret_key(SECRET_FILE_PATH)

print(app.secret_key)

# Class to store user info
# UserMixin provides us with an `id` field and the necessary
# methods (`is_authenticated`, `is_active`, `is_anonymous` and `get_id()`)


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




def register():
    print()





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

