import os
import pathlib
import secrets
import bcrypt
import threading
from pygments import highlight
from pygments.filters import KeywordCaseFilter, NameHighlightFilter
from pygments.formatters.html import HtmlFormatter
from pygments.lexers import SqlLexer
from pygments import token


"""
File for storing various utility functions.
"""


def pygmentize(text):
    tls = threading.local()
    if not hasattr(tls, 'formatter'):
        tls.formatter = HtmlFormatter(nowrap=True)
    if not hasattr(tls, 'lexer'):
        tls.lexer = SqlLexer()
        tls.lexer.add_filter(NameHighlightFilter(names=['GLOB'], tokentype=token.Keyword))
        tls.lexer.add_filter(NameHighlightFilter(names=['text'], tokentype=token.Name))
        tls.lexer.add_filter(KeywordCaseFilter(case='upper'))
    return f'<span class="highlight">{highlight(text, tls.lexer, tls.formatter)}</span>'


def get_secret_key(file_path: pathlib.Path):
    if not os.path.exists(file_path):
        # If the secret file does not exist, generate a new one,
        # store it in the flask object and write to file
        # Generates a 256 bit long secret key.
        with file_path.open("w") as secret_file:
            secret_key = secrets.token_hex(32)
            secret_file.write(secret_key)
    else:
        with file_path.open("r") as secret_file:
            secret_key = secret_file.read()
    return secret_key


def create_hashed_and_salted_password(plaintext_password: str | bytes) -> bytes:
    """
    Function for salting and hashing a plaintext password.

    :param plaintext_password:
    :return:
    """
    # Bcrypt generates and inserts the salt into the password itself
    if isinstance(plaintext_password, str):
        plaintext_password = bytes(plaintext_password, encoding='utf-8')
    return bcrypt.hashpw(plaintext_password, bytes(bcrypt.gensalt()))


def check_password(plaintext_password: str | bytes, hashed_password: str | bytes) -> bool:
    """
    Performs the password validation.

    :param plaintext_password: The plaintext password string.
    :param hashed_password:
    :return: A bool of whether the password matched.
    """
    if isinstance(plaintext_password, str):
        plaintext_password = bytes(plaintext_password, encoding='utf-8')

    if isinstance(hashed_password, str):
        hashed_password = bytes(hashed_password, encoding='utf-8')

    return bcrypt.checkpw(plaintext_password, hashed_password)
