#!venv/bin/python

import json
import datetime
import urllib2
import os

from flask import Flask
from flask import request
from flask import render_template
import MySQLdb

from flask import Flask, redirect, url_for, session, request
from flask_oauth import OAuth


SECRET_KEY = 'a3eb0e9b167d5524d1c84fe68bdc2271'
DEBUG = True
FACEBOOK_APP_ID = '292895004174602'
FACEBOOK_APP_SECRET = 'a3eb0e9b167d5524d1c84fe68bdc2271'


app = Flask(__name__)  # Creates a Flask application object
app.debug = DEBUG
app.secret_key = SECRET_KEY
oauth = OAuth()

facebook = oauth.remote_app('facebook',
    base_url='https://graph.facebook.com/',
    request_token_url=None,
    access_token_url='/oauth/access_token',
    authorize_url='https://www.facebook.com/dialog/oauth',
    consumer_key=FACEBOOK_APP_ID,
    consumer_secret=FACEBOOK_APP_SECRET,
    request_token_params={'scope': 'email'}
)


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
    return facebook.authorize(callback=url_for('facebook_authorized',
        next=request.args.get('next') or request.referrer or None,
        _external=True))


@app.route('/login/authorized')
@facebook.authorized_handler
def facebook_authorized(resp):
    if resp is None:
        return 'Access denied: reason=%s error=%s' % (
            request.args['error_reason'],
            request.args['error_description']
        )
    session['oauth_token'] = (resp['access_token'], '')
    me = facebook.get('/me')
    return 'Logged in as id=%s name=%s redirect=%s' % \
        (me.data['id'], me.data['name'], request.args.get('next'))

@facebook.tokengetter
def get_facebook_oauth_token():
    return session.get('oauth_token')


@app.route("/logout/", methods=['GET', 'POST'])
def logout():
    global authenticated
    authenticated = False
    return index()

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
