"""Forms for the Kudos system."""

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SelectField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo


class RegistrationForm(FlaskForm):
    """User registration form."""
    username = StringField("Username", validators=[DataRequired(), Length(min=3, max=80)])
    email = StringField("Email", validators=[DataRequired(), Email(), Length(max=255)])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField("Confirm Password", validators=[DataRequired(), EqualTo("password")])
    department = StringField("Department", validators=[Length(max=100)])
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


class ReportForm(FlaskForm):
    """Form for reporting inappropriate kudos."""
    reason = TextAreaField("Reason for Report", validators=[DataRequired(), Length(min=5, max=500)])
    submit = SubmitField("Submit Report")


class ModerationForm(FlaskForm):
    """Form for moderation reason."""
    reason = StringField("Reason", validators=[Length(max=255)])
    submit = SubmitField("Confirm")
