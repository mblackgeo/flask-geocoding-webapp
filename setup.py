from setuptools import setup, find_packages

setup(
    name="geocoderapp",
    version="0.0.1",
    url="https://github.com/mblackgeo/flask-geocoding-webapp.git",
    author="Martin Black",
    author_email="mblack@sparkgeo.com",
    description="A simple geocoding webapp using Flask and Folium",
    packages=find_packages(),
    package_data={'templates': ['*']},
    install_requires=[],  # TODO
)
