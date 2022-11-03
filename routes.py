from flask_login import login_required
import forms
import apsw
import flask
from flask import abort, make_response, render_template, request, send_from_directory
from json import dumps
from pygments.formatters import HtmlFormatter
from markupsafe import escape
from database import DATABASE_NAME
from utils import pygmentize


"""
File for handling the URL routes.
"""

routes = flask.Blueprint('routes', __name__)


@routes.route('/send', methods=['POST', 'GET'])
def send():
    """
    Route responsible for sending a message.

    :return:
    """
    try:
        connection = apsw.Connection(DATABASE_NAME)
        cursor = connection.cursor()
        sender = request.args.get('sender') or request.form.get('sender')
        message = request.args.get('message') or request.args.get('message')
        # FIXME this has an SQL injection vuln.
        if not sender or not message:
            return f'ERROR: missing sender or message'
        stmt = f"INSERT INTO messages (sender, message) values ('{sender}', '{message}');"
        result = f"Query: {pygmentize(stmt)}\n"
        cursor.execute(stmt)
        return f'{result}ok'
    except apsw.Error as e:
        return f'{result}ERROR: {e}'


@routes.get('/search')
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
            result = f'{result}   {dumps(row)}\n'
        c.close()
        return result
    except apsw.Error as e:
        return f'{result}ERROR: {e}', 500


@routes.get('/announcements')
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
    except apsw.Error as e:
        return {'error': f'{e}'}

@routes.route('/')
@routes.route('/index.html')
@login_required
def home():
    return send_from_directory(routes.root_path, 'index.html', mimetype='text/html')


@routes.get('/account')
@login_required
def account():
    return render_template('account.html')

@routes.get('/coffee/')
def nocoffee():
    abort(418)


@routes.route('/coffee/', methods=['POST', 'PUT'])
def gotcoffee():
    return "Thanks!"


@routes.get('/highlight.css')
def highlightStyle():
    css_data = HtmlFormatter(nowrap=True).get_style_defs('.highlight')
    resp = make_response(css_data)
    resp.content_type = 'text/css'
    return resp
