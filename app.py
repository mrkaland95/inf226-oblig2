import os
import pathlib
import secrets
import bcrypt
import auth
import flask
import sys
import apsw
import flask_login
from flask import Flask, abort, request, send_from_directory, make_response, render_template
from werkzeug.datastructures import WWWAuthenticate
from http import HTTPStatus
import database
from json import dumps, loads
from flask_login import LoginManager

users = {'alice': {'password': 'password123', 'token': 'tiktok'},
         'bob': {'password': 'bananas'}
         }


def main():
    """
    Initializes the actual app.
    :return:
    """
    # Set up app
    app = Flask(__name__)
    # The secret key enables storing encrypted session data in a cookie (make a secure random key for this!)
    secret_key_path = pathlib.Path('/.secret_key')
    app.secret_key = auth.get_secret_key(secret_key_path)
    database.init_db()
    return app



# This method is called whenever the login manager needs to get
# the User object for a given user id



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






