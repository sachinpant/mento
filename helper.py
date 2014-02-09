#! engine/bin/python2.7

from flask import Flask, request, send_file, jsonify, Response
from flask.ext.sqlalchemy import SQLAlchemy 

app = Flask(__name__)
# set up the config and database
app.config.from_object('config')
db = SQLAlchemy(app)
