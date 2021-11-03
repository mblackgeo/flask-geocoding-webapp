from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, SubmitField
from wtforms.validators import DataRequired


class GeocodeLocationForm(FlaskForm):
    """Form for entering a location and selecting a geolocation provider"""

    location = StringField("Enter location to geocode", [DataRequired()])

    provider = SelectField(
        "Select geocoding provider",
        choices=[("mapbox", "Mapbox"), ("nominatim", "OpenStreetMap Nominatim")],
    )

    submit = SubmitField("Submit")
