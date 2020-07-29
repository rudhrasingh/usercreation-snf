from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed,FileRequired
from wtforms import StringField, PasswordField, SubmitField, BooleanField,SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo

class UserCreation(FlaskForm):
    username = StringField('Username',validators=[DataRequired(), Length(min=5, max=20)])
    region = StringField('Account',validators=[DataRequired(), Length(min=5, max=20)])
    rolename = SelectField(u'Role',choices=[('ACCOUNTADMIN', 'ACCOUNTADMIN'), ('SECURITYADMIN', 'SECURITYADMIN')])   
    password = PasswordField('Password', validators=[DataRequired()])
    usersfile = FileField('Upload users data file ', validators=[FileRequired(),FileAllowed(['txt', 'csv','dat'])])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Submit')