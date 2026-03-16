"""Forms for the Kudos system."""

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SelectField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError


class RegistrationForm(FlaskForm):
    """User registration form."""
    username = StringField("Username", validators=[DataRequired(), Length(min=3, max=80)])
    email = StringField("Email", validators=[DataRequired(), Email(), Length(max=120)])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField("Confirm Password", validators=[DataRequired(), EqualTo("password")])
    submit = SubmitField("Register")


class LoginForm(FlaskForm):
    """User login form."""
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Log In")


class KudosForm(FlaskForm):
    """Form for giving kudos."""
    receiver_id = SelectField("Select Colleague", coerce=int, validators=[DataRequired()])
    message = TextAreaField("Your Message", validators=[DataRequired(), Length(min=1, max=500)])
    submit = SubmitField("Send Kudos 🎉")


class ModerationForm(FlaskForm):
    """Form for moderation reason."""
    reason = StringField("Reason", validators=[Length(max=255)])
    submit = SubmitField("Confirm")
