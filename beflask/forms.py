from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    PasswordField,
    BooleanField,
    SubmitField,
)
from wtforms.validators import (
    DataRequired,
    Length,
)


class LoginForm(FlaskForm):
    username = StringField(
        "Username", validators=[DataRequired(), Length(1, 20)]
    )
    password = PasswordField(
        "Password", validators=[DataRequired(), Length(4, 150)]
    )
    remember_me = BooleanField("Remember me")
    submit = SubmitField()


class BenchmarkSelect(FlaskForm):
    submit = SubmitField("Select")
