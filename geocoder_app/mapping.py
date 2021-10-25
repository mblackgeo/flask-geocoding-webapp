import folium
from geopy.geocoders import get_geocoder_for_service


def geocode_location(user_agent, provider, api_key, location):
    # get the selected geocoder
    cls = get_geocoder_for_service(provider)

    # Configure and set API key if mapbox
    config = {"user_agent": user_agent}
    if provider == "mapbox":
        config["api_key"] = api_key

    # Return the lat/lng
    geolocator = cls(**config)
    location = geolocator.geocode(location)
    return (location.latitude, location.longitude)


def create_map(app, location, provider):
    # geocode the location
    user_agent = app.name
    api_key = app.config.get("MAPBOX_ACCESS_TOKEN")
    point = geocode_location(user_agent, provider, api_key, location)

    # create the leaflet map using folium centred on the geocoded point
    fmap = folium.Map(
        location=point,
        zoom_start=14,
        tiles="cartodbpositron",
    )

    # add the point to the map
    popup = folium.Popup(f"{location}<br/>{point}", show=True)
    folium.Marker(location=point, popup=popup).add_to(fmap)

    return fmap._repr_html_()
