import time
import flask
import flask_login
import database
import app
import forms
import utils
from flask import flash,  render_template, Blueprint, current_app
from http import HTTPStatus
from flask_login import login_user, logout_user, login_required, current_user, user_logged_in
from werkzeug.datastructures import WWWAuthenticate
from base64 import b64decode
from utils import is_safe_url

"""
File for handling the login side of the app.
"""

auth = Blueprint('auth', __name__)


@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = forms.RegistrationForm()
    redirect_to_register = render_template('register.html', title='Wannabe Discord Register', form=form)
    # if form.is_submitted():
    #     print(f'Received form: {"invalid" if not form.validate() else "valid"} {form.form_errors} {form.errors}')

    if not form.validate_on_submit():
        return redirect_to_register

    username = form.username.data
    password = form.password.data

    hashed_password = utils.create_hashed_and_salted_password(password)

    if not database.add_user_to_db(username, hashed_password):
        flash('The account already exists, choose another username.')
        time.sleep(0.05)
        return redirect_to_register
    current_app.logger.info(f'Created account with username: {username} and password: {hashed_password}')
    flash(f'Account created. You should now be able to log in.')
    return flask.redirect(flask.url_for('auth.login'))

@auth.route('/login', methods=['GET', 'POST'])
def login():

    if current_user.is_authenticated:
        flask.redirect(flask.url_for('routes.home'))

    form = forms.LoginForm()
    redirect_to_login = render_template('login.html', title='Wannabe Discord Login', form=form)

    if form.validate_on_submit():

        username = form.username.data
        password = form.password.data

        valid_login = database.validate_login(username, password)

        if not valid_login:
            flash('Login was unsuccessful. Please check username and password.')
            time.sleep(0.05)
            return redirect_to_login

        user = user_loader(username)

        if not user:
            flash('Something went wrong when loading the user on the server.')
            return redirect_to_login

        # automatically sets logged in session cookie
        login_user(user)
        flask.flash('Logged in successfully.')
        next_request = flask.request.args.get('next')

        # Implementation of the safe URL function in utils.
        if not is_safe_url(next_request):
            return flask.abort(400)
        return flask.redirect(next_request or flask.url_for('routes.home'))
    return redirect_to_login


@auth.route('/logout')
@login_required
def logout():
    if user_logged_in:
        logout_user()
        flash('Logged out successfully.')
        time.sleep(0.05)
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
        if database.validate_login(uid, passwd):
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
    found_user = database.get_user_data_by_name(uid)

    if not found_user:
        return

    user = User()
    user.id = found_user[1]
    return user


class User(flask_login.UserMixin):
    time_created: str
    pass


