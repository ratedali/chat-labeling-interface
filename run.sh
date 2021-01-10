#!/bin/sh
exec env FLASK_APP=src/app.py FLASK_ENVIRONMENT=development flask run -h 0.0.0.0
