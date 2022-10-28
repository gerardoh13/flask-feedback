from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, EmailField, TextAreaField
from wtforms.validators import InputRequired, Length


class UserForm(FlaskForm):
    username = StringField("Username: ", validators=[InputRequired(), Length(min=1, max=20)], render_kw={"placeholder": "username"})
    password = PasswordField("Password: ", validators=[InputRequired()], render_kw={"placeholder": "password!"})
    email = EmailField("Email: ", validators=[InputRequired(), Length(min=1, max=50)], render_kw={"placeholder": "email"})
    first_name = StringField("First Name: ", validators=[InputRequired(), Length(min=1, max=30)], render_kw={"placeholder": "first name"})
    last_name = StringField("Last Name: ", validators=[InputRequired(), Length(min=1, max=30)], render_kw={"placeholder": "last name"})

class LoginForm(FlaskForm):
    username = StringField("Username: ", validators=[InputRequired()], render_kw={"placeholder": "username"})
    password = PasswordField("Password: ", validators=[InputRequired()], render_kw={"placeholder": "password"})

class FeedbackForm(FlaskForm):
    title = StringField("Title: ", validators=[InputRequired(), Length(min=1, max=100)], render_kw={"placeholder": "title"})
    content = TextAreaField("Content: ", validators=[InputRequired()], render_kw={"placeholder": "content"})
