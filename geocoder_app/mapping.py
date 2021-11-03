from typing import Tuple

import folium
from flask import Flask
from geopy.geocoders import get_geocoder_for_service


def geocode_location(user_agent: str, provider: str, api_key: str, location: str) -> Tuple[float, float]:
    """Geocode a location using a specific provider

    Parameters
    ----------
    user_agent : str
        Name of user agent used when making a request to ``provider``
    provider : str
        Name of provider to use. In theory this is anything supported by
        `geopy.geocoders.get_geocoder_for_service`, however in practice only
        OpenStreetMap Nominatim and Mapbox are used
    api_key : str
        If using Mapbx, the API key
    location : str
        Location to geocode

    Returns
    -------
    Tuple[float, float]
        Lat, Lng returned from the geocoder
    """

    # get the selected geocoder
    cls = get_geocoder_for_service(provider)

    # Configure and set API key if mapbox
    config = {"user_agent": user_agent}
    if provider == "mapbox":
        config["api_key"] = api_key

    # Return the lat/lng
    geolocator = cls(**config)
    geocoded_location = geolocator.geocode(location)
    return (geocoded_location.latitude, geocoded_location.longitude)


def create_map(app: Flask, location: str, provider: str) -> str:
    """Create a map by geocoding a location using a specific provider

    Parameters
    ----------
    app : Flask
        Flask application. Used to extract the app name as the user agent
        when performing geocoding
    location : str
        Location to geocode
    provider : str
        Provider to use. Choose Nominatim, Mapbox

    Returns
    -------
    str
        Folium map rendered as HTML suitable for embedding as an iframe
    """
    # geocode the location
    user_agent = app.name
    api_key = app.config.get("MAPBOX_ACCESS_TOKEN", "")
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
