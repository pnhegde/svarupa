#!venv/bin/python

import json
import datetime
import urllib2
import os

from flask import Flask
from flask import request
from flask import render_template
import MySQLdb

app = Flask(__name__)  # Creates a Flask application object
db = MySQLdb.connect("localhost","root","kde","EventMDB" )
cursor = db.cursor()
authenticated = False

@app.route("/", methods=['GET', 'POST'])
def index():
    return render_template('index.html')


@app.route("/about/", methods=['GET', 'POST'])
def about():
    return render_template('about.html')

@app.route("/login/", methods=['GET', 'POST'])
def login():
    return render_template('login.html')

@app.route("/authentication/", methods=['GET', 'POST'])
def authentication():
    cursor = db.cursor()
    name = urllib2.unquote(request.form['username'])
    passwd = urllib2.unquote(request.form['passwd'])
    query = "select * from User where u_name='"+name+"' and password='"+passwd+"'"
    cursor.execute(query);
    print "row size is --------->>>"
    print cursor.rowcount
    if cursor.rowcount == 1 :
        row = cursor.fetchone()
        print "success"
        global authenticated
        authenticated = True
        return createNewEvent()
    else:
        print "Authentication failed"
        return(" Wrong username of password")

@app.route("/createNewEvent/", methods=['GET', 'POST'])
def createNewEvent():
    if authenticated == True:
        return render_template('create_event.html')
    else:
        return login()



if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
