"""Route declaration."""
from flask import current_app as app
from flask import render_template, jsonify, request

from geocoder_app.forms import GeocodeLocationForm
from geocoder_app.mapping import create_map


@app.route("/", methods=["GET", "POST"])
def home():
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
def health():
    return jsonify({"status": "ok"})
