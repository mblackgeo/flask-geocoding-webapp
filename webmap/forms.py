from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, SubmitField
from wtforms.validators import DataRequired


class GeocodeLocationForm(FlaskForm):
    location = StringField('Enter location to geocode using Nominatim', [DataRequired()])
    provider = SelectField(
        'Select geocoding provider',
        choices=[('mapbox', 'Mapbox'), ('osm', 'OpenStreetMap Nominatim')],
    )
    submit = SubmitField('Submit')
