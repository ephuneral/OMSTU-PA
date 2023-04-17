from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from wtforms import FileField, SubmitField


class UpdateAccountForm(FlaskForm):
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Update')

