"""Route declaration."""
import folium
from flask import current_app as app
from flask import render_template, jsonify, request
from geopy.geocoders import Nominatim

from webmap.forms import GeocodeLocationForm


@app.route('/', methods=["GET", "POST"])
def home():
    form = GeocodeLocationForm()

    if request.method == 'POST':
        return create_map(request.form.get('location'))

    return render_template(
        'index.html',
        title="Flask WebMap Sandbox",
        description="Testing out rendering webmaps with Flask and Folium",
        form=form,
    )


def create_map(location):
    # geocode the location
    geolocator = Nominatim(user_agent=app.name)
    location = geolocator.geocode(location)
    point = (location.latitude, location.longitude)

    # create the leaflet map using folium centred on the geocoded point
    fmap = folium.Map(
        location=point,
        zoom_start=14,
        tiles='cartodbpositron',
    )

    # add the point to the map
    popup = folium.Popup(f"{location}<br/>{point}", show=True)
    folium.Marker(location=point, popup=popup).add_to(fmap)

    return fmap._repr_html_()


@app.route("/health")
def health():
    return jsonify({'status': 'ok'})
