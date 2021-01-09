#!/bin/sh
cd src/
export FLASK_APP=app.py
export FLASK_ENVIRONMENT=production
exec flask run
