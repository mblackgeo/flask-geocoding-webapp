# Flask Geocoding Webapp

The example webmap application uses [Flask](https://flask.palletsprojects.com/en/2.0.x/) along with [Folium](https://python-visualization.github.io/folium/index.html) to geocode a given location (using [geopy](https://github.com/geopy/geopy) via [Nominatim](https://nominatim.openstreetmap.org/)) and display the result as a [LeafletJS](https://leafletjs.com/) map.

![Example usage](/screenshots/example.gif)

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
./scripts/build && ./scripts/run
```

Once either of these is running, browse to the application: [http://0.0.0.0:5000](http://0.0.0.0:5000)

## Deploying to AWS

To deploy the container to AWS [copilot](https://aws.github.io/copilot-cli/docs/getting-started/install/) is used to run the container using [AWS App Runner](https://eu-west-1.console.aws.amazon.com/apprunner/home?region=eu-west-1#/welcome). The usage is as follows:

```shell
copilot init  # answer a few questions, say "yes" to test deployment and wait for AWS App Engine to do it's magic
# this takes around 10 minutes after which copilot should emit a URL with your service

# TODO production deployment
# TODO pipeline creation

# Tear down everything with
copilit app delete
```

This app has only been deployed in a test environment, however copilot can (and should) be used for production deployments or even with CI/CD. More details are in the [introductory blogpost](https://aws.amazon.com/blogs/containers/introducing-aws-copilot/).

## TODO

* [Handle secrets](https://aws.github.io/copilot-cli/docs/developing/secrets/) when building with copilot
* Production deployment with copilot
* [Automatic pipeline deployment](https://aws.github.io/copilot-cli/docs/concepts/pipelines/) using copilot
* Form validation
