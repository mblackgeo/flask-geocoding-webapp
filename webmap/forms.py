from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


class GeocodeLocationForm(FlaskForm):
    """Contact form."""
    location = StringField('Location', [DataRequired()])
    submit = SubmitField('Submit')
