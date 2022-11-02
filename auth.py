import bcrypt
import flask_login
from http import HTTPStatus
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
import main
"""
File for handling the login side of the app.
"""


login_manager = flask_login.LoginManager()
login_manager.init_app(main.app)
login_manager.login_view = "login"

@login_manager.request_loader
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
    abort(HTTPStatus.UNAUTHORIZED, www_authenticate=WWWAuthenticate('Basic realm=inf226, Bearer'))






def create_hashed_and_salted_password(plaintext_password):
    """

    :param plaintext_password:
    :return:
    """
    # Bcrypt generates and inserts the salt into the password itself.
    return bcrypt.hashpw(plaintext_password, bcrypt.gensalt())


def check_password(plaintext_password: str | bytes, hashed_password: str | bytes) -> bool:
    """
    :param plaintext_password: The plaintext password string.
    :param hashed_password:
    :return: A bool of whether the password matched.
    """
    if isinstance(plaintext_password, str):
        plaintext_password = bytes(plaintext_password)
    if isinstance(hashed_password, str):
        plaintext_password = bytes(plaintext_password)
    return bcrypt.checkpw(plaintext_password, hashed_password)


class LoginForm(FlaskForm):
    username = StringField('Username')
    password = PasswordField('Password')
    submit = SubmitField('Submit')


@login_manager.user_loader
def user_loader(user_id):
    # TODO 1. chance this to load a user from a database. Including hashing and salting.
    if user_id not in users:
        return

    # For a real app, we would load the User from a database or something
    user = User()
    user.id = user_id
    return user