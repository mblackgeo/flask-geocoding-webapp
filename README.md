# flask-webmap-sandbox

## Geocoding application example

The example webmap application uses [Flask](https://flask.palletsprojects.com/en/2.0.x/) along with [Folium](https://python-visualization.github.io/folium/index.html) to geocode a given location (using [geopy](https://github.com/geopy/geopy) via [Nominatim](https://nominatim.openstreetmap.org/)) and display the result as a [LeafletJS](https://leafletjs.com/) map.

## Usage

Before running a new `.env` file should be created following the `.env.example` file.

On a local machine, a new virtualenv can be created and the debug version of the app can ran as follows:

```shell
conda create -n flaskwebapp python=3.7
pip install -r requirements.txt
python run.debug.py
```

Alternatively the containerised version, which uses the [Bjoern](https://github.com/jonashaag/bjoern) WSGI server can be launched as follows:

```shell
./build.sh && ./run-local.sh
```

Once either of these is running, browse to the application: [http://0.0.0.0:5000](http://0.0.0.0:5000)

## TODO

* Docker build secrets using [Docker BuildKit](https://docs.docker.com/develop/develop-images/build_enhancements/)
* Form validation