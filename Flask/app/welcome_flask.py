#!/usr/bin/env python

import flask
import os
import sqlite3
import pandas as pd
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
from flask import abort,  jsonify

App = flask.Flask(__name__)


mydb = '../../sqlStart/Abstracts_DB.db'
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
    with App.open_resource('../creatEmpUsers.py', mode='r') as f:
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

@App.route('/aboutme/')
def aboutme():
    """ TODO: Displays the page about the coolest person around.
    """
    
    return flask.render_template('index.html')
@App.route('/welcome/<name>/')
def welcome(name):
    """ Displays the welcome screen.
    """
    return flask.render_template('welcome.html', name=name)

@App.route('/users')
def getUsers():
    '''TODO: USERS FOR ABSTRACTS_DB'''
    with sqlite3.connect('../EmpData.sql') as con:
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        cur.execute("SELECT * FROM User")
        rows = cur.fetchall();
        
        keys = rows[0].keys()

        #return df
        return render_template('tables.html', title = 'users' , rows = rows, keys = keys)


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

@App.route("/jsonTotal/<table>", methods=('GET',))
def getjsonTotal(table):
    '''Return Jsonified table SELECT *'''
    
    with sqlite3.connect("../../sqlStart/Abstracts_DB.db") as con:
        con.row_factory = dict_factory
        cur = con.cursor()
        cur.execute("SELECT * FROM '%s'" %table)
        entries = cur.fetchall()
        #data = {'data' : entries}
    
    return jsonify(dict(data=entries))

@App.route("/totals/<table>", methods = ('GET',))
def jasonhtml(table):
    '''Display the total table'''
    html = 'jsonTotal' + table + '.html'
    print html
    return render_template(html)

if __name__ == '__main__':
   
    App.debug=True
    
    App.run()
