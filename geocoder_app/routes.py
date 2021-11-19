"""Route declaration."""
import requests
from flask import Response
from flask import current_app as app
from flask import jsonify, make_response, redirect, render_template, request, url_for

from geocoder_app.forms import GeocodeLocationForm
from geocoder_app.mapping import create_map


@app.route("/", methods=["GET", "POST"])
def home() -> str:
    """Render the homepage of the website and handle both GET and POST

    GET requests will render the GeocodeLocationForm
    POST requests will extract details from a submitted GeocodeLocationForm,
    call whichever geocoding api was requested and render a map of the result

    Returns
    -------
    str
        HTML of page to display at "/"
    """
    form = GeocodeLocationForm()

    if request.method == "POST":
        map_content = create_map(
            app,
            location=request.form.get("location"),
            provider=request.form.get("provider"),
        )

        return render_template(
            "map.html",
            title="Flask WebMap Sandbox",
            map_content=map_content,
        )

    else:
        return render_template(
            "index.html",
            title="Flask WebMap Sandbox",
            description="Testing out rendering webmaps with Flask and Folium",
            form=form,
        )


@app.route("/health")
def health() -> Response:
    """Return a JSON response containing status OK. Used for automatic health checks

    Returns
    -------
    flask.Response
        200 OK response
    """
    return jsonify({"status": "ok"})


@app.route("/user")
def user() -> Response:
    """
    Calls the Cognito User Info endpoint
    """

    url = app.config.get("USER_INFO_URL")
    if url:
        access_token = request.headers.get("x-amzn-oidc-accesstoken")
        response = requests.get(url, headers={"Authorization": f"Bearer {access_token}"})
        return response.json()

    return jsonify({"status": "Cognito not in use"})


@app.route("/logout")
def logout() -> Response:
    """
    This handles the logout action for the app if Cognito is used, else
    redirects to the homepage
    """
    logout_url = app.config.get("LOGOUT_URL")

    if logout_url:
        # Looks a little weird, but this is the only way to get an HTTPS redirect
        response = make_response(redirect(app.config.get("LOGOUT_URL", f"https://{request.host}/")))

        # Invalidate the session cookie
        response.set_cookie("AWSELBAuthSessionCookie-0", "empty", max_age=-3600)

        return response

    return redirect(url_for("home"))
