#!venv/bin/python

import json
import datetime
import bson.json_util
import urllib2
import os

from flask import Flask
from flask import request
from flask import render_template


app = Flask(__name__)  # Creates a Flask application object

@app.route("/", methods=['GET', 'POST'])
def index():
    return render_template('index.html')


@app.route("/about/", methods=['GET', 'POST'])
def about():
    return render_template('about.html')

@app.route("/login/", methods=['GET', 'POST'])
def login():
    return render_template('login.html')

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
