#!venv/bin/python

import json
import datetime
import urllib2
import os

from flask import Flask
from flask import request
from flask import render_template
import _mysql

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
current_user = ""
facebook = oauth.remote_app('facebook',
    base_url='https://graph.facebook.com/',
    request_token_url=None,
    access_token_url='/oauth/access_token',
    authorize_url='https://www.facebook.com/dialog/oauth',
    consumer_key=FACEBOOK_APP_ID,
    consumer_secret=FACEBOOK_APP_SECRET,
    request_token_params={'scope': 'email'}
)


db = _mysql.connect("localhost","root","kde","EventMDB" )

@app.route("/index/")
@app.route("/")
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


@app.route("/createEvent/", methods=['GET', 'POST'])
def createNewEvent():
    if not session['logged_in']:
        return redirect(url_for('login'))
    return render_template('create_event.html')


@app.route('/faceboo_authorized')
@facebook.authorized_handler
def facebook_authorized(resp):
    next_url = request.args.get('next') or url_for('index')
    if resp is None or 'access_token' not in resp:
        return redirect(next_url)
    session['logged_in'] = True
    session['facebook_token'] = (resp['access_token'], '')
    me = facebook.get('/me')
    print '---------------------------------------------------------'
    print me.data
    print '---------------------------------------------------------'
    global current_user
    uid = me.data['id']
    current_user = uid
    name =  me.data['name'] if me.data.get('name') else "Noname"
    bio = me.data['bio'] if me.data.get('bio') else "No bio"
    fb_id = me.data['link'] if me.data.get('link') else "no link"
    email = me.data['email'] if me.data.get('email') else "no email"
    gender = me.data['gender'] if me.data.get('gender') else "unknown"
    q = 'SELECT * FROM User WHERE u_id='+uid+';'
    db.query(q);
    r = db.store_result()
    print r.num_rows()
    if not r.num_rows() :
        q = "INSERT INTO User VALUES ('"+uid+"','"+name+"','"+bio+"','"+fb_id+"','"+email+"','"+gender+"');"
        db.query(q)

    next_url = 'http://0.0.0.0:5000/createEvent/'
    return redirect(next_url)

@facebook.tokengetter
def get_facebook_token():
    return session.get('facebook_token')


@app.route("/logout/", methods=['GET', 'POST'])
def logout():
    pop_login_session()
    return redirect(url_for('index'))

def pop_login_session():
    session.pop('logged_in', None)
    session.pop('facebook_token', None)

@app.route("/submitNewEvent", methods=['GET','POST'])
def  submitNewEvent():
    ename = urllib2.unquote(request.form['name']) if urllib2.unquote(request.form['name']) else "Anonymous event"
    cat = urllib2.unquote(request.form['category']) if urllib2.unquote(request.form['category']) else 'unknown'
    date = urllib2.unquote(request.form['date']) if urllib2.unquote(request.form['date']) else None
    time = urllib2.unquote(request.form['time']) if urllib2.unquote(request.form['time']) else None
    loc = urllib2.unquote(request.form['loc']) if urllib2.unquote(request.form['loc']) else "unknown"
    desc = urllib2.unquote(request.form['desc']) if urllib2.unquote(request.form['desc']) else None
    q = "INSERT INTO CreateEvent(e_name,e_loc,e_date,e_time,e_category,u_id,e_desc) VALUES ('"+ename+"','"+loc+"','"+date+"','"+time+"','"+cat+"','"+current_user+"','desc');"
    print q
    db.query(q);
    return redirect(url_for('index'))

@app.route("/events", methods=['GET','POST'])
def events():
    cat = urllib2.unquote(request.form['category']) if urllib2.unquote(request.form['category']) else 'all'
    if  cat == "all" :
        q = 'SELECT * FROM CreateEvent'
        db.query(q)
        result = db.store_result()
        if result.num_rows() :
            print result.



# @app.route("/authentication/", methods=['GET', 'POST'])
# def authentication():
#     cursor = db.cursor()
#     name = urllib2.unquote(request.form['username'])
#     passwd = urllib2.unquote(request.form['passwd'])
#     query = "select * from User where u_name='"+name+"' and password='"+passwd+"'"
#     cursor.execute(query);
#     print "row size is --------->>>"
#     print cursor.rowcount
#     if cursor.rowcount == 1 :
#         row = cursor.fetchone()
#         print "success"
#         global authenticated
#         authenticated = True
#         return createNewEvent()
#     else:
#         print "Authentication failed"
#         return(" Wrong username of password")


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
