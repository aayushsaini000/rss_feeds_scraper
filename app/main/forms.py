from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField
from wtforms.validators import DataRequired

class EmptyForm(FlaskForm):
    submit = SubmitField('Submit')


class RSSFeedForm(FlaskForm):
    feed_url = StringField('feed_url', validators=[DataRequired()])
    category = StringField('category', validators=[DataRequired()])
