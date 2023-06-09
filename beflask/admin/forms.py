from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    PasswordField,
    BooleanField,
    SubmitField,
    SelectField,
)
from wtforms.validators import (
    DataRequired,
    Length,
    EqualTo,
    Email,
    ValidationError,
)
from beflask.models import User


class UserForm(FlaskForm):
    username = StringField(
        "Username", validators=[DataRequired(), Length(1, 20)]
    )
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField(
        "Password", validators=[DataRequired(), Length(4, 150)]
    )
    password2 = PasswordField(
        "Password",
        validators=[DataRequired(), Length(4, 150), EqualTo("password")],
    )
    admin = BooleanField("Admin")
    benchmark_id = SelectField("Benchmark", coerce=int)

    submit = SubmitField()

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        message = "Already taken. Please use a different one."
        if user is not None:
            if self.user_id is None:
                raise ValidationError(message)
            else:
                if user.id != int(self.user_id):
                    raise ValidationError(message)

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        message = "Already taken. Please use a different one."
        if user is not None:
            if self.user_id is None:
                raise ValidationError(message)
            else:
                if user.id != int(self.user_id):
                    raise ValidationError(message)


class UpdatePasswordForm(FlaskForm):
    password = PasswordField(
        "Password", validators=[DataRequired(), Length(4, 150)]
    )
    password2 = PasswordField(
        "Password",
        validators=[DataRequired(), Length(4, 150), EqualTo("password")],
    )
    submit = SubmitField()


class BenchmarkForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired(), Length(1, 20)])
    description = StringField(
        "Description", validators=[DataRequired(), Length(1, 20)]
    )
    folder = StringField("Folder", validators=[DataRequired(), Length(1, 20)])
    submit = SubmitField()
