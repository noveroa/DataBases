#!/usr/bin/env python

import flask
import os
import sqlite3
import pandas as pd
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
from flask import abort,  jsonify
import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from cStringIO import StringIO
import base64

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

def getTotalPD():
    with sqlite3.connect(mydb) as con:
        sqlcmd = "SELECT * FROM ABSTRACTSTOTAL"
        df = pd.read_sql_query(sqlcmd, con)
        print df.shape
        
    return df

@App.route('/mmmmPie2')
def getPie2(start = getTotalPD()):
    import matplotlib.pyplot as plt

    df = pd.DataFrame(start[["Conf", "year"]])
    keys = list(df['Conf'].unique())
    
    fig, axes = plt.subplots(nrows=len(keys) + 1, ncols=1,
                             sharex=False, figsize = (15, 20), 
                            )
    fig = df.groupby(['Conf'])["Conf"].count().plot(kind = 'pie', colormap = 'ocean', 
                                                subplots = True, ax = axes[0] )    
    for i, conference in enumerate(keys):
        fig = df.query('Conf == "%s"' % conference).groupby('year').count().plot(kind = 'pie', 
                                                                           ax = axes[i+1],
                                                                           colormap = 'ocean',
                                                                           subplots = True)
                                                    
                                                                          
    html = '''
    <html>
    <head>
         <h1> Conferences by year %s</h1>
    </head>
    <body> 
        
        <img src="data:image/png;base64,{}" />
        
    </body>
    </html>
    '''%keys
    
    io = StringIO()
    plt.savefig(io, format='png')
    data = base64.encodestring(io.getvalue())

    return html.format(data)
    


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
    """ Displays the page about the coolest person around.
    """
    return flask.render_template('aboutMe.html')

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
    
    with sqlite3.connect(mydb) as con:
        con.row_factory = dict_factory
        cur = con.cursor()
        cur.execute("SELECT * FROM '%s'" %table)
        entries = cur.fetchall()
        #data = {'data' : entries}
    
    return jsonify(dict(data=entries))
@App.route("/totals/<table>", methods = ('GET',))
def jasonhtml(table):
    '''Display the total table'''
    html = 'totaltables/jsonTotal' + table + '.html'
    return render_template(html)


@App.route("/jsonContents", methods = ('GET',))
def getContents():
    with sqlite3.connect(mydb) as con:
    
        cursor = con.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        mytables = (cursor.fetchall())
        myt = []
        for x in mytables[1:]:
            table_entry = {}
            table_name = x[0]
            table_entry['name'] = table_name
            html = 'http://127.0.0.1:5000/totals/%s' % table_name
            table_entry['html'] = "<a href='%s'<button>click</button>></a>" %html
            table_entry['count'] = cursor.execute("SELECT COUNT(*) FROM %s"%table_name).fetchone()[0]
        
            myt.append(table_entry) 
            
    return jsonify(dict(data = myt))
    #render_template('/jsonContents.html')
@App.route("/contents", methods = ('GET',))
def jsonContents():
    '''Display the total table'''
    return render_template('/jsonContents.html')

@App.route("/conf2", methods = ('GET',))
def group(start = getTotalPD()):
    dfs = {}
    df = pd.DataFrame(start[["Conf", "year"]])
    keys = list(df['Conf'].unique())

    dfs['TOTAL'] = dict(data = df.groupby(['Conf'])["Conf"].count().to_dict())
    for conference in keys:
        dfs[conference] = df.query('Conf == "%s"' % conference).groupby('year').count().to_dict()
                                                    
                                                                        
    return jsonify(data = dfs)
@App.route("/confsyear", methods = ('GET',))
def jsonConfs():
    '''Display the total table'''
    return render_template('/conferences2.html')

if __name__ == '__main__':
   
    App.debug=True
    
    App.run()
    
