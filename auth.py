import time

import flask
import flask_login
import database
import app
import forms
import utils
from flask import abort, flash, redirect, render_template, Blueprint, request, current_app
from http import HTTPStatus
from flask_login import login_user, logout_user
from werkzeug.datastructures import WWWAuthenticate
from base64 import b64decode

"""
File for handling the login side of the app.
"""

auth = Blueprint('auth', __name__)


@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = forms.RegistrationForm()
    redirect_to_register = render_template('register.html', title='Wannabe Discord Register', form=form)
    if form.is_submitted():
        print(f'Received form: {"invalid" if not form.validate() else "valid"} {form.form_errors} {form.errors}')
        # print(request.form)

    if not form.validate_on_submit():
        return redirect_to_register

    username = form.username.data
    password = form.password.data

    # if not password == secondary_password:
    #     flash(f'Specified passwords do not match. Try again.')
    #     return redirect_to_register

    hashed_password = utils.create_hashed_and_salted_password(password)
    if not database.add_user_to_db(username, hashed_password):
        flash('The account already exists, choose another username.')
        time.sleep(0.05)
        return redirect_to_register

    flash(f'Account created. You should now be able to log in.')
    return flask.redirect(flask.url_for('auth.login'))


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = forms.LoginForm()
    redirect_to_login = render_template('login.html', title='Wannabe Discord Login', form=form)

    if not form.validate_on_submit():
        current_app.logger.info(f'Invalid login attempt.')
        return redirect_to_login

    username = form.username.data
    password = form.password.data

    valid_login = database.validate_login(username, password)
    f'{valid_login = }'

    if not valid_login:
        flash('Login was unsuccessful. Please check username and password.')
        return redirect_to_login

    user = user_loader(username)

    if not user:
        flash('Something went wrong when loading the user on the server.')
        return redirect_to_login

    # automatically sets logged in session cookie
    login_user(user)
    flask.flash('Logged in successfully.')
    next_request = flask.request.args.get('next')

    # is_safe_url should check if the url is safe for redirects.
    # See http://flask.pocoo.org/snippets/62/ for an example.
    if False and not is_safe_url(next_request):
        return flask.abort(400)

    return flask.redirect(next_request or flask.url_for('routes.home'))


@auth.route('/logout')
def logout():
    logout_user()
    flash('Logged out successfully.')
    return flask.redirect(flask.url_for('auth.login'))


# This method is called to get a User object based on a request,
# for example, if using an api key or authentication token rather
# than getting the user name the standard way (from the session cookie)
@app.login_manager.request_loader
def request_loader(request):
    # print(request.headers)
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
        print(f'{uid = }')
        print(f'Basic auth: {uid}:{passwd}')

        if database.validate_login(uid, passwd):  # and check_password(u.password, passwd):
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


@app.login_manager.user_loader
def user_loader(uid):
    found_user = database.get_user_data(uid)

    if not found_user:
        return

    user = User()
    user.id = found_user[0]
    user.username = found_user[1]
    return user


class User(flask_login.UserMixin):
    username: str
    time_created: str

    pass


