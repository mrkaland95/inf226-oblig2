import flask
import flask_login
import database
import app
import forms
from flask import abort, flash, redirect, render_template, Blueprint, request
from http import HTTPStatus
from flask_login import login_user, logout_user
from werkzeug.datastructures import WWWAuthenticate
from base64 import b64decode


"""
File for handling the login side of the app.
"""

# FIXME remove this once implemented the database.
users = {'alice': {'password': 'password123', 'token': 'tiktok'},
         'bob': {'password': 'bananas'}}


auth = Blueprint('auth', __name__)


# Class to store user info
# UserMixin provides us with an `id` field and the necessary
# methods (`is_authenticated`, `is_active`, `is_anonymous` and `get_id()`)
class User(flask_login.UserMixin):
    pass


@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = forms.RegistrationForm()
    redirect_to_register = render_template('./register.html', form=form)
    if form.is_submitted():
        print(f'Received form: {"invalid" if not form.validate() else "valid"} {form.form_errors} {form.errors}')
        print(request.form)

    if not form.validate_on_submit():
        return redirect_to_register

    username = form.username.data
    password = form.password.data
    secondary_password = form.password_confirm.data

    temp = 0
    if temp:
        return flask.url_for('home')
    return redirect_to_register

@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = forms.LoginForm()
    redirect_to_login = render_template('./login.html', form=form)
    if form.is_submitted():
        print(f'Received form: {"invalid" if not form.validate() else "valid"} {form.form_errors} {form.errors}')
        print(request.form)

    if not form.validate_on_submit():
        return redirect_to_login

    username = form.username.data
    password = form.password.data

    valid_login = database.validate_login(username, password)

    if not valid_login:
        flash('Login was unsuccessful. Please check username and password.')
        return redirect_to_login

    user = user_loader(username)

    # automatically sets logged in session cookie
    logged_user = login_user(user)

    flask.flash('Logged in successfully.')

    next_request = flask.request.args.get('next')

    # TODO have a look at this.
    # is_safe_url should check if the url is safe for redirects.
    # See http://flask.pocoo.org/snippets/62/ for an example.
    if False and not is_safe_url(next_request):
        return flask.abort(400)

    return flask.redirect(next_request or flask.url_for('home'))

@auth.route('/logout')
def logout():
    logout_user()
    return flask.redirect(flask.url_for('home'))


# This method is called to get a User object based on a request,
# for example, if using an api key or authentication token rather
# than getting the user name the standard way (from the session cookie)
@app.login_manager.request_loader
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
    flask.abort(HTTPStatus.UNAUTHORIZED, www_authenticate=WWWAuthenticate('Basic realm=inf226, Bearer'))


# # This method is called to get a User object based on a request,
# # for example, if using an api key or authentication token rather
# # than getting the user name the standard way (from the session cookie)
# @app.login_manager.request_loader
# def request_loader(request):
#     # Even though this HTTP header is primarily used for *authentication*
#     # rather than *authorization*, it's still called "Authorization".
#     auth = request.headers.get('Authorization')
#
#     # If there is not Authorization header, do nothing, and the login
#     # manager will deal with it (i.e., by redirecting to a login page)
#     if not auth:
#         return
#
#     (auth_scheme, auth_params) = auth.split(maxsplit=1)
#     auth_scheme = auth_scheme.casefold()
#     if auth_scheme == 'basic':  # Basic auth has username:password in base64
#         (uid, passwd) = b64decode(auth_params.encode(errors='ignore')).decode(errors='ignore').split(':', maxsplit=1)
#         print(f'Basic auth: {uid}:{passwd}')
#         u = users.get(uid)
#         if u:  # and check_password(u.password, passwd):
#             return user_loader(uid)
#     elif auth_scheme == 'bearer':  # Bearer auth contains an access token;
#         # an 'access token' is a unique string that both identifies
#         # and authenticates a user, so no username is provided (unless
#         # you encode it in the token – see JWT (JSON Web Token), which
#         # encodes credentials and (possibly) authorization info)
#         print(f'Bearer auth: {auth_params}')
#         for uid in users:
#             if users[uid].get('token') == auth_params:
#                 return user_loader(uid)
#     # For other authentication schemes, see
#     # https://developer.mozilla.org/en-US/docs/Web/HTTP/Authentication
#
#     # If we failed to find a valid Authorized header or valid credentials, fail
#     # with "401 Unauthorized" and a list of valid authentication schemes
#     # (The presence of the Authorized header probably means we're talking to
#     # a program and not a user in a browser, so we should send a proper
#     # error message rather than redirect to the login page.)
#     # (If an authenticated user doesn't have authorization to view a page,
#     # Flask will send a "403 Forbidden" response, so think of
#     # "Unauthorized" as "Unauthenticated" and "Forbidden" as "Unauthorized")
#     abort(HTTPStatus.UNAUTHORIZED, www_authenticate=WWWAuthenticate('Basic realm=inf226, Bearer'))


@app.login_manager.user_loader
def user_loader(user_name):
    # THIS IS ONLY CALLED IF THE USER IS ALREADY AUTHENTICATED
    found_user = database.get_user_data_from_db(user_name)

    if not found_user:
        return found_user

    user = User()
    user.id = found_user
    return user


