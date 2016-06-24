#!/usr/bin/env python

import flask
import os
import sqlite3
import pandas as pd
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
from flask import abort,  jsonify

import images as images
images = reload(images)

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

def getTotalPD(db):
    with sqlite3.connect(db) as con:
        sqlcmd = "SELECT * FROM ABSTRACTSTOTAL"
        df = pd.read_sql_query(sqlcmd, con)
        print ('Datbase : ', df.shape)
        
    return df


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
    

@App.route("/contents", methods = ('GET',))
def jsonContents():
    '''Display the total table'''
    return render_template('/jsonContents.html')




@App.route("/jsonContentsconf", methods = ('GET',))
def getContentsconf():
    with sqlite3.connect(mydb) as con:
        sqlcmd = "SELECT Conf, Year FROM ABSTRACTSTOTAL"
        df = pd.read_sql_query(sqlcmd, con)
        myt = []
    
        
        conferences = list(df['Conf'].unique())
    
   
        for conf in conferences:
        
            entry = {}
            entry['conf'] = conf
        
        
            subDF = df.query('Conf == "%s"' % conf).groupby('year').count()
            entry['counts'] = subDF.to_html()
            
            image = images.getPieOne(subDF, conf)
            entry['Pie']  = image
        
            image2 = images.getBar(subDF, conf)
            entry['Bar'] = image2
        
            myt.append(entry)
    
    return jsonify(dict(data = myt))

@App.route("/jsonconfyrpapers/<year>/<conf>", methods=('GET',))
def getPapersConfYr(year, conf):
    with sqlite3.connect(mydb) as con:
        sqlcmd = "SELECT pubYear, confName, paperID, title, abstract FROM PAPER"
        PAPdf = pd.read_sql_query(sqlcmd, con)
    
        group = PAPdf.groupby(['pubYear', 'confName'], axis = 0)
    
        try:
            subgroup =  group.get_group((int(year), conf))
        
            mytable = []
            for idx in subgroup.index.get_values():
                entry = {}
                entry['paperID'] = subgroup.loc[idx]['paperID']
                entry['Title'] = subgroup.loc[idx]['title']
                entry['Abstract'] = subgroup.loc[idx]['abstract']    
                mytable.append(entry)
       
            return jsonify( dict(data = mytable))
        
        except:
           
            entry = {'paperID': 'NoConference',
                     'Title': 'NoConference',
                     'Abstract': 'NoConference',
                     }
            mytable = [entry]
            return jsonify(dict(data = mytable))

@App.route("/confyrpapers/<year>/<conf>", methods = ('GET',))
def jsonConfYrPaper(year, conf):
    '''Display the papers from a given year and conference table'''
    
    return render_template('/ConfYrPaper.html', entry = [year, conf])

@App.route("/contentsconf", methods = ('GET',))
def jsonContentsconf():
    '''Display the total table'''
    
    return render_template('/jsonContentsconf.html')


def getPapersKWgroup(grouper):
    with sqlite3.connect(mydb) as con:
        sqlcmd = "SELECT paperID, title, confName, pubYear FROM PAPER "
        paperdf = pd.read_sql_query(sqlcmd, con)
        sqlcmd2 = "SELECT paperID, keyword FROM PAPERKEY "
        kwdf = pd.read_sql_query(sqlcmd2, con)
        
        merged = kwdf.merge(paperdf, on = 'paperID')
        
        subgrp = merged.groupby(grouper)
        
        return subgrp
    
@App.route("/papers/keywords", methods = ('GET',))    
def getPaperKW():
    data_frame = getPapersKWgroup('paperID')
    entries = []
    for each in data_frame.groups:
        entry = {}
        entry['paperID'] = each
        entry['keywords'] = [str(eval(key)) for key in data_frame.get_group(each)['keyword']]
        entries.append(entry)
    return jsonify(dict(data = entries))

@App.route("/paperKWs.html", methods = ('GET',))
def jsonPaperKW():
    '''Display the total table'''
    
    return render_template('/paperKWs.html')

@App.route('/findaConf',methods=('GET', ))
def findaconf():
    return render_template('/findaConf.html')



if __name__ == '__main__':
   
    App.debug=True
    
    App.run()
    
