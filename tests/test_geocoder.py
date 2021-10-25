from geocoder_app.forms import GeocodeLocationForm


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200


def test_home_get(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "Enter location to geocode" in str(response.data)


def test_home_post(client, mocker):
    # mock the call so we don't hit a real api
    mocker.patch(
        "geocoder_app.mapping.geocode_location",
        return_value=(1.0, 1.0),
    )

    with client.session_transaction():
        form = GeocodeLocationForm(location="asd", provider="mapbox")
        assert form.validate() is True

        response = client.post("/", data=form.data)
        assert response.status_code == 200
        assert 'iframe id="map-canvas"' in str(response.data)


def test_home_post_incorrect_form(client, mocker):
    # mock the call so we don't hit a real api
    mocker.patch(
        "geocoder_app.mapping.geocode_location",
        return_value=(1.0, 1.0),
    )

    # expect form to be invalid with incorrect provider
    with client.session_transaction():
        form = GeocodeLocationForm(location="asd", provider="asd")
        assert form.validate() is False
