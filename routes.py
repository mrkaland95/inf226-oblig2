import flask_login
import database
import forms
import apsw
import flask
from flask_login import login_required
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


@login_required
@routes.route('/')
@routes.route('/index.html')
@routes.route('/home')
def home():
    return send_from_directory(routes.root_path, 'templates/index.html', mimetype='text/html')


@login_required
@routes.route('/send', methods=['POST', 'GET'])
def send():
    """
    Route responsible for sending a message.

    :return:
    """
    try:
        current_user = flask_login.current_user.id
        sender = request.args.get('sender') or request.form.get('sender')
        message = request.args.get('message') or request.args.get('message')
        if not sender or not message:
            return f'ERROR: missing sender or message'
        database.send_message(current_user, message)
        return f'{message} - ok'
    except apsw.Error as e:
        return f'ERROR: {e}'


@login_required
@routes.get('/search')
@routes.get('/messages')
@routes.get('/messages/int:<ID>')
def search():
    current_user = flask_login.current_user.id
    print(f'{current_user = }')
    search_parameter = request.args.get('q') or request.form.get('q') or '*'
    # stmt = '''SELECT * FROM messages
    #           INNER JOIN users u on u.user_id = messages.sender_id
    #           WHERE message_content GLOB (?)'''
    #           # WHERE user_name = (?)
    #           # '''

    stmt = '''SELECT '''

    result = f"Query: {pygmentize(stmt)}\n"
    try:
        connection = apsw.Connection(DATABASE_NAME)
        c = connection.execute(stmt, (current_user, ))
        rows = c.fetchall()
        result = result + 'Result:\n'
        for row in rows:
            result = f'{result}   {dumps(row)}\n'
        c.close()
        return result
    except apsw.Error as e:
        return f'{result}ERROR: {e}', 500

@login_required
@routes.get('/announcements')
def announcements():
    query = f"SELECT author,content FROM announcements;"
    try:
        connection = apsw.Connection(DATABASE_NAME)
        cursor = connection.cursor()
        c = cursor.execute(query)
        announcements = []
        for row in c:
            announcements.append({'sender': escape(row[0]), 'message': escape(row[1])})
        return {'data': announcements}
    except apsw.Error as e:
        return {'error': f'{e}'}


@login_required
@routes.get('/account')
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

