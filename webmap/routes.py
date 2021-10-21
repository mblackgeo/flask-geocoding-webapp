"""Route declaration."""
from flask import current_app as app
from flask import render_template, jsonify, request

from webmap.forms import GeocodeLocationForm
from webmap.mapping import create_map


@app.route('/', methods=["GET", "POST"])
def home():
    form = GeocodeLocationForm()

    if request.method == 'POST':
        return render_template(
            'map.html',
            title="Flask WebMap Sandbox",
            map_content=create_map(app, request.form.get('location')),
        )

    else:
        return render_template(
            'index.html',
            title="Flask WebMap Sandbox",
            description="Testing out rendering webmaps with Flask and Folium",
            form=form,
        )


@app.route("/health")
def health():
    return jsonify({'status': 'ok'})
