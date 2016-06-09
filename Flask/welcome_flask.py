#!/usr/bin/env python

import flask
import os
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash

App = flask.Flask(__name__)
App.config.from_object(__name__)

# Load default config and override config from an environment variable
App.config.update(dict(
    DATABASE=os.path.join(App.root_path, 'flaskr.db'),
    SECRET_KEY='development key',
    USERNAME='admin',
    PASSWORD='default'
))
App.config.from_envvar('FLASKR_SETTINGS', silent=True)

def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(App.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv

def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db

def init_db():
    db = get_db()
    with App.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()

@App.cli.command('initdb')
def initdb_command():
    """Initializes the database."""
    init_db()
    print 'Initialized the database.'

@App.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()
        
@App.route('/')
def index():
    """ Displays the index page accessible at '/'
    """
    return flask.render_template('index.html')


@App.route('/welcome/<name>/')
def welcome(name):
    """ Displays the page greats who ever comes to visit it.
    """
    return flask.render_template('welcome.html', name=name)

@App.route('/enternew')
def new_user():
    return render_template('user.html')

@App.route('/addrec',methods = ['POST', 'GET'])
def addrec():
    if request.method == 'POST':
        try:
            userID = request.form['userID']
            userName = request.form['userName']
            password = request.form['pw']
            
            with sqlite3.connect('EmpData') as con:
                cur = con.cursor()
                cur.execute("INSERT INTO USERS VALUES('userID','userName', 'password')")
            
                con.commit()
                msg = "Record successfully added"
        except:
            con.rollback()
            msg = "error in insert operation"
            
        finally:
            return render_template("result.html",msg = msg)
            con.close()

@App.route('/list')
def list():
    con = sqlite3.connect("EmpData")
    con.row_factory = sqlite3.Row
    print('opened db')
    cur = con.cursor()
    cur.execute("SELECT * FROM User")
    
    rows = cur.fetchall();
    
    return render_template("list.html",rows = rows)
         
            
@App.route("/Authenticate")
def Authenticate():
    username = request.args.get('UserName')
    password = request.args.get('Password')
    cursor = sqlite3.connect().cursor()
    cursor.execute("SELECT * from User where Username='" + username + "' and Password='" + password + "'")
    data = cursor.fetchone()
    if data is None:
         return "Username or Password is wrong"
    else:
         return "Logged in successfully"

if __name__ == '__main__':
   
    App.debug=True
    App.run()
    
    