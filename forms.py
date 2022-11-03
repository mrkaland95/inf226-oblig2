import wtforms
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField

"""
File for handling the various forms
"""


class LoginForm(FlaskForm):
    username = StringField('Username')
    password = PasswordField('Password')
    submit = SubmitField('Submit')


class RegisterForm(FlaskForm):
    username = StringField('Username')
    password = PasswordField('Password')
    password_secondary = PasswordField('PasswordSecondary')
    submit = SubmitField('Submit')


