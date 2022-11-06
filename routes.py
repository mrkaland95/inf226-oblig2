import flask_login
import database
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


@routes.route('/')
@routes.route('/index.html')
@routes.route('/home')
@login_required
def home():
    return render_template('index.html', mimetype='text/html')


@routes.route('/new', methods=['POST', 'GET'])
@login_required
def send():
    """
    Route responsible for sending a message.
    :return:
    """
    sender = flask_login.current_user.id
    message = request.args.get('message') or request.form.get('message')
    recipient = request.args.get('recipient') or request.form.get('recipient')
    if not message or recipient:
        return f'ERROR: missing message or recipient'
    database.send_message(sender, recipient, message)
    return f'sent message: {message} - ok'


@routes.get('/messages')
@routes.get('/messages/int:<ID>')
@login_required
def search():
    current_user = flask_login.current_user.id
    result = ""


    rows = database.get_users_messages(current_user)
    for row in rows:
        result = f'{dumps(row)}\n'
    return result



@routes.get('/announcements')
# @login_required
# def announcements():
#     query = f"SELECT author,content FROM announcements;"
#     try:
#         connection = apsw.Connection(DATABASE_NAME)
#         cursor = connection.cursor()
#         c = cursor.execute(query)
#         announcements = []
#         for row in c:
#             announcements.append({'sender': escape(row[0]), 'message': escape(row[1])})
#         return {'data': announcements}
#     except apsw.Error as e:
#         return {'error': f'{e}'}

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


