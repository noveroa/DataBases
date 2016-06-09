#!/usr/bin/env python

import flask
import os
import sqlite3
import pandas as pd
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash

App = flask.Flask(__name__)
mydb = '../sqlStart/Abstracts_DB.db'
def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(mydb)
    rv.row_factory = sqlite3.Row
    return rv

def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, mydb):
        g.sqlite_db = connect_db()
    return g.sqlite_db

def init_db():
    db = get_db()
    with App.open_resource('creatEmpUsers.py', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()
#init myabstracts_db?

@App.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, mydb):
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

@App.route('/users')
def getUsers():
    with sqlite3.connect('EmpData') as con:
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        cur.execute("SELECT * FROM User")
        rows = cur.fetchall();
        
        # Check resulting pandas DF shape
        #print df.shape
        
        #return df
        return render_template('user.html', rows = rows)

@App.route('/confs')
def getConfs():
    with sqlite3.connect(mydb) as con:
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        cur.execute("SELECT * FROM CONFERENCES")
        rows = cur.fetchall();
        
        # Check resulting pandas DF shape
        #print df.shape
        
        #return df
        return render_template('conf.html', rows = rows)

if __name__ == '__main__':
   
    App.debug=True
    App.run()
    
    