"""Route declaration."""
from flask import Response
from flask import current_app as app
from flask import jsonify, render_template, request

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
