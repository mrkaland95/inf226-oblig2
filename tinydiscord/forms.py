from flask_wtf import FlaskForm
from wtforms import BooleanField, StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, ValidationError, EqualTo


"""
File for handling the various forms in the templates.
"""


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Log in')


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8, max=20)])
    # Used validators to make sure that the passwords match.
    password_confirm = PasswordField('Confirm Password',
                                     validators=[DataRequired(), Length(min=8, max=20), EqualTo('password')])

    submit = SubmitField('Sign Up')
