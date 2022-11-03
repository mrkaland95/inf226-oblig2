import forms
import apsw
import flask

from flask import abort, make_response, request
from json import dumps
from pygments.formatters import HtmlFormatter
from markupsafe import escape
from database import DATABASE_NAME
from utils import pygmentize


"""
File for handling the URL routes.
"""

routes = flask.Blueprint('routes', __name__)
cssData = HtmlFormatter(nowrap=True).get_style_defs('.highlight')



# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     form = forms.LoginForm()
#     redirect_on_failure = flask.render_template('./auth/login.html', form=form)
#     if form.is_submitted():
#         print(f'Received form: {"invalid" if not form.validate() else "valid"} {form.form_errors} {form.errors}')
#         print(request.form)
#
#     if not form.validate_on_submit():
#         return redirect_on_failure
#
#     username = form.username.data
#     password = form.password.data
#
#     valid_login = validate_login(username, password)
#
#     if not valid_login:
#         return redirect_on_failure
#
#     user = user_loader(username)
#
#     # automatically sets logged in session cookie
#     logged_user = login_user(user)
#
#     flask.flash('Logged in successfully.')
#
#     next = flask.request.args.get('next')
#
#     # is_safe_url should check if the url is safe for redirects.
#     # See http://flask.pocoo.org/snippets/62/ for an example.
#     if False and not is_safe_url(next):
#         return flask.abort(400)
#
#     return flask.redirect(next or flask.url_for('index'))


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


@routes.get('/coffee/')
def nocoffee():
    abort(418)


@routes.route('/coffee/', methods=['POST', 'PUT'])
def gotcoffee():
    return "Thanks!"

@routes.get('/highlight.css')
def highlightStyle():
    resp = make_response(cssData)
    resp.content_type = 'text/css'
    return resp

