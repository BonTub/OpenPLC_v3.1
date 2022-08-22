# https://flask-wtf.readthedocs.io/en/0.15.x/form/

#pip install Flask-Uploads # adjust for werkzeug submodules
from flask_uploads import (
    UploadSet,
    configure_uploads,
    IMAGES,
    UploadNotAllowed
    )

images = UploadSet('images', IMAGES)

from flask_wtf.file import (
    FileField,
    FileAllowed,
    FileRequired,
)

from flask_wtf import FlaskForm
from flask_wtf import Form
#from wtforms.fields import *

from wtforms import (
    StringField,
    PasswordField,
    BooleanField,
    FloatField,
    DateField,
    DecimalField,
    DateTimeField,
    IntegerField,
    TextAreaField,
    ValidationError,
    validators,
    SubmitField,
)

from wtforms.validators import (
    InputRequired,
    DataRequired,
    Length,
    EqualTo,
    Email,
    Regexp,
    Optional,
    )

#import email_validator
#from flask_login import current_user

import models
#from models import User
#from models import Setting

class SignupForm(Form):
    sample_file = FileField(u'Your favorite file')
    name = StringField(u'Your name', validators=[DataRequired()])
    password = StringField(u'Your favorite password', validators=[DataRequired()])
    email = StringField(u'Your email address', validators=[Email()])
    birthday = DateField(u'Your birthday')

    a_float = FloatField(u'A floating point number')
    a_decimal = DecimalField(u'Another floating point number')
    a_integer = IntegerField(u'An integer')

    now = DateTimeField(u'Current time', description='...for no particular reason')

    eula = BooleanField(u'I did not read the terms and conditions',
                        validators=[DataRequired('You must agree to not agree!')])

    submit = SubmitField(u'Signup')


class UploadForm(FlaskForm):
    upload = FileField('image', validators=[
        FileRequired(),
        FileAllowed(images, 'Images only!')
    ])

class LoginForm(FlaskForm):
    email = StringField(validators=[InputRequired(), Email(), Length(1, 64)])
    pwd = PasswordField(validators=[InputRequired(), Length(min=8, max=72)])
    # Placeholder labels to enable form rendering
    username = StringField(
        validators=[Optional()]
    )


class RegisterForm(FlaskForm):
    username = StringField(
        validators=[
            InputRequired(),
            Length(3, 20, message="Please provide a valid name"),
            Regexp(
                "^[A-Za-z][A-Za-z0-9_.]*$",
                0,
                "Usernames must have only letters, " "numbers, dots or underscores",
            ),
        ]
    )
    email = StringField(validators=[InputRequired(), Email(), Length(1, 64)])
    pwd = PasswordField(validators=[InputRequired(), Length(8, 72)])
    cpwd = PasswordField(
        validators=[
            InputRequired(),
            Length(8, 72),
            EqualTo("pwd", message="Passwords must match !"),
        ]
    )

    def validate_email(self, email):
        if User.query.filter_by(email=email.data).first():
            raise ValidationError("Email already registered!")

    def validate_uname(self, uname):
        if User.query.filter_by(username=username.data).first():
            raise ValidationError("Username already taken!")
    
    
    # return '''
    # <!doctype html>
    # <title>Upload new File</title>
    # <h1>Upload new File</h1>
    # <form method=post enctype=multipart/form-data>
    #   <input type=file name=file>
    #   <input type=submit value=Upload>
    # </form>
    # '''
    
class SearchForm(FlaskForm):
    """
    We expect search queries to come externally, thus we don't want CSRF
    even though it's set up on the base form.
    """
    class Meta:
        # This overrides the value from the base form.
        csrf = False
    
class ProgramForm(FlaskForm):
    # remember to include in <form ..> : enctype="multipart/form-data"
    file = FileField(validators=[FileRequired()])
    name = StringField(validators=[InputRequired(), Length(1, 80)])
    description = StringField(validators=[InputRequired(), Length(1, 80)])
    date_upload = IntegerField(validators=[InputRequired()])
    date = DateField('Upload Date', format='%Y-%m-%d')
    submit_field = SubmitField('Upload')

    startdate_field = DateField('Start Date', format='%Y-%m-%d')
    enddate_field = DateField('End Date', format='%Y-%m-%d')
    submit_field2 = SubmitField('Next')
     

class SettingForm(FlaskForm):
    key = StringField(validators=[InputRequired(), Length(1, 64)])
    value = StringField(validators=[InputRequired(),  Length(1, 64)])
# Placeholder labels to enable form rendering
    value = StringField(
        validators=[Optional()]
    )
