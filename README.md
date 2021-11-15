# Flask Geocoding Webapp

The example webmap application uses [Flask](https://flask.palletsprojects.com/en/2.0.x/) along with [Folium](https://python-visualization.github.io/folium/index.html) to geocode a given location (using [geopy](https://github.com/geopy/geopy) via [Mapbox](https://docs.mapbox.com/api/search/geocoding/) or [Nominatim](https://nominatim.openstreetmap.org/)) and display the result as a [LeafletJS](https://leafletjs.com/) map.

![Example usage](/example.gif)

## Usage

:exclamation: Before running a new `.env` file should be created following the `.env.example` file.

On a local machine, a new virtualenv can be created and the debug version of the app can ran as follows:

```shell
conda create -n flaskwebapp python=3.7
pip install -r requirements.txt
python run.debug.py
```

Alternatively the containerised version, which uses the [Bjoern](https://github.com/jonashaag/bjoern) WSGI server can be launched as follows:

```shell
# apt-get install libev-dev
./scripts/build && ./scripts/run
```

Once either of these is running, browse to the application: [http://0.0.0.0:5000](http://0.0.0.0:5000)

## Development

For local development, pre-commit should be installed and the application can be installed as editable along with the dev requirements:

```shell
pre-commit install
pip install -e .
pip install -r requirements-dev.txt
pre-commit install
```

* [Pytest](https://docs.pytest.org/en/6.2.x/) is used for the functional tests of the application (see `/tests`).
* Code is linted using [flake8](https://flake8.pycqa.org/en/latest/) with `--max-line-length=120`
* Code formatting is validated using [Black](https://github.com/psf/black)
* [pre-commit](https://pre-commit.com/) is used to run these checks locally before files are pushed to git
* The [Github Actions pipeline](.github/workflows/pipeline.yml) also runs these checks and tests

## Deployment

Deployment to AWS is handled by the AWS Cloud Development Kit (CDK) using AWS Elastic Container Service (ECS). All code is in [`/infra`](/infra).

However as this an is a simple standalone container, [AWS copilot](https://aws.github.io/copilot-cli) was previously used for initial deployment. It could also be used for production deployments and to generate CI/CD pipelines. More details are in the [introductory blogpost](https://aws.amazon.com/blogs/containers/introducing-aws-copilot/).
