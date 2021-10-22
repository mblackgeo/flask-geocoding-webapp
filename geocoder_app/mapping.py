import folium
from geopy.geocoders import get_geocoder_for_service


def create_map(app, location, provider):
    # get the selected geocoder
    app.logger.debug(f'Getting geocoder for : {provider}')
    cls = get_geocoder_for_service(provider)

    # Configure and set API key if mapbox
    config = {'user_agent': app.name}
    if provider == 'mapbox':
        config['api_key'] = app.config.get('MAPBOX_ACCESS_TOKEN')

    geolocator = cls(**config)

    # geocode the location
    app.logger.debug(f'Geocoding location : {location}')
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
