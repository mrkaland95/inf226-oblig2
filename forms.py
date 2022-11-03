from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length


"""
File for handling the various forms in the templates.
"""


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Submit')


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', PasswordField('Confirm Password',
                                                       validators=[DataRequired(), Length(min=8, max=20)]))
    password_confirm = PasswordField('Confirm Password',
                                     validators=[DataRequired(), Length(min=8, max=20)])
    submit = SubmitField('Submit')
