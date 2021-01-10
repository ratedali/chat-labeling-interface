#!/bin/sh
cd src/
env FLASK_APP=app.py FLASK_ENVIRONMENT=development flask run
