#!/bin/bash

cd webserver
. .venv/bin/activate
FLASK_APP=routes.py
FLASK_DEBUG=1
FLASK_ENV=development
flask run --debugger
