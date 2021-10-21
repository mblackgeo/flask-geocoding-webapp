from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


class GeocodeLocationForm(FlaskForm):
    """Contact form."""
    location = StringField('Enter location to geocode using Nominatim', [DataRequired()])
    submit = SubmitField('Submit')
