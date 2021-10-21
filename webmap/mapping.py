import folium
from geopy.geocoders import Nominatim


def create_map(app, location):
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
