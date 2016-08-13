#!/usr/bin/env python

import flask
import sys, os
import sqlite3
import pandas as pd
import numpy as np

from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
from flask import abort,  jsonify

import images as images
images = reload(images)
import wordcloud_generator2 as wcg
wcg = reload(wcg)

App = flask.Flask(__name__)
#ip = "http://" + str(request.remote_addr) + ":5000"

mydb = 'scripts/Abstracts_aug12.db'

def connect_db():
    """
    Connects to the specific database.
    """
    rv = sqlite3.connect(mydb)
    rv.row_factory = sqlite3.Row
    return rv

def get_db():
    """
    Opens a new database connection if there is none yet for the
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

def getTotalPD(db):
    """ 
    : param db str : address of the data_base to query
    : output : pandas dataframe represenaton of sql database
    """
    with sqlite3.connect(db) as con:
        sqlcmd = "SELECT * FROM ABSTRACTSTOTAL"
        df = pd.read_sql_query(sqlcmd, con)
        print ('Database : ', df.shape)
        
    return df

@App.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, mydb):
        g.sqlite_db.close()
        
@App.route('/')
def index():
    """ 
    Renders aboutme page html for '/' the index page
    """
    return flask.render_template('index.html', entry = mydb)

@App.route("/get_my_ip", methods=["GET"])
def get_my_ip():
    return str(request.remote_addr)
@App.route('/aboutme/')
def aboutme():
    """ 
    Renders aboutme page html for sit author
    """
    return flask.render_template('extras/aboutMe.html')

@App.route('/welcome/<name>/')
def welcome(name):
    """ 
    : param name str : name of person surfing the site
    Renders welcome html for person...
    """
    return flask.render_template('extras/welcome.html', name=name)

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
        return render_template('extras/tables.html', 
                               title = 'users' , rows = rows, keys = keys)

def dict_factory(cursor, row):
    '''
    : 
    : output : Returns a json dictionary of rows and columns
    ''' 
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


'''
                                                TOTAL TABLES
''' 
@App.route("/jsonTotal/<table>", methods=('GET',))
def getjsonTotal(table):
    '''
    : param Table
    : output : Returns a json dictionary of the given table's attributes
    ''' 
    with sqlite3.connect(mydb) as con:
        con.row_factory = dict_factory
        cur = con.cursor()
        cur.execute("SELECT * FROM '%s'" %table)
        entries = cur.fetchall()
        #data = {'data' : entries}
    
    return jsonify(dict(data=entries))

@App.route("/totals/<table>", methods = ('GET',))
def jasonhtml(table):
    '''
    Renders getjsonTotal(table) as html
    '''
    html = 'totaltables/jsonTotal' + table + '.html'
    return render_template(html)


@App.route("/jsonContents", methods = ('GET',))
def getContents():
    '''
    : param NONE
    : output : Returns a json dictionary of the table names, 
               entry counts, and links to tables 
               of all table names in the database
    ''' 
    with sqlite3.connect(mydb) as con:
    
        cursor = con.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        mytables = (cursor.fetchall())
        myt = []
        for x in mytables:
            table_entry = {}
            table_name = x[0]
            table_entry['name'] = table_name
            html = "/totals/%s" % table_name
            table_entry['html'] = "<a href='%s'<button>click</button>></a>" %html
            table_entry['count'] = cursor.execute("SELECT COUNT(*) FROM %s"%table_name).fetchone()[0]
        
            myt.append(table_entry) 
            
    return jsonify(dict(data = myt))
    

@App.route("/contents", methods = ('GET',))
def jsonContents():
    '''
    Renders getContents() as html
    '''
    return render_template('/totaltables/jsonContents.html')

'''
                                        CONFERENCE BREAKDOWNS AND FUNCTIONS - BY YEAR
'''


@App.route("/jsonContentsconf", methods = ('GET',))
def getContentsconf():
    '''
    : param NONE
    : output : Returns a json dictionary of each conference with 
                pie and bar chart visualizations of each broken down by year
    '''  
    with sqlite3.connect(mydb) as con:
        sqlcmd = "SELECT Conf, Year FROM ABSTRACTSTOTAL"
        df = pd.read_sql_query(sqlcmd, con)
        myt = []
    
        
        conferences = list(df['Conf'].unique())
    
   
        for conf in conferences:
        
            entry = {}
            entry['conf'] = conf
        
        
            subDF = df.query('Conf == "%s"' % conf).groupby('year').count()
            
            entry['counts'] = subDF.reset_index().to_html(classes = 'counts')
            
            image = images.getPieOne(subDF, conf)
            entry['Pie']  = image
            
            subDF.reset_index(inplace = True)
            image2 = images.getBar(subDF, 
                                    conf, 
                                    xaxis = 'year', yaxis = 'Conf', 
                                    orientation = "v",
                                    ylabel = 'Count', xlabel = 'Publication Year')
            
            entry['Bar'] = image2
        
            myt.append(entry)
    
    return jsonify(dict(data = myt))

@App.route("/contentsconf", methods = ('GET',))
def jsonContentsconf():
    '''
    Renders getContentsconf() as html
    '''
    return render_template('/conferences/jsonContentsconf.html')


@App.route("/jsonconfyrpapers/<year>/<conf>", methods=('GET',))
def getPapersConfYr(year, conf):
    '''
    : param year str/int : Year of a conference
    : param conf str : Valid Conference Name (WICSA, ECSA, QoSA)
    : output : Returns a json dictionary of paperID, 
               title, Abstract for given conf, year
    '''  
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
    '''
    Renders getPapersConfYr(year, conf) as html
    '''
    return render_template('/conferences/ConfYrPaper.html', 
                           entry = [year, conf])


@App.route("/jsonconfyrbreakdown", methods=('GET',))
def getPapersConfYrTable():
    '''
    : param NONE
    : output : Returns a json dictionary of conferences, 
               publication years, links to each conf/yr 
               papers, top keywords, and authors
    '''    
    with sqlite3.connect(mydb) as con:
        sqlcmd = "SELECT pubYear, confName, paperID, title, abstract FROM PAPER"
        PAPdf = pd.read_sql_query(sqlcmd, con)
    
        group = PAPdf.groupby(['pubYear', 'confName'], axis = 0)
        entries = []
        for year, conf in group.groups.keys():
            entry = {}
            entry['conference'] = conf
            entry['year'] = year
            
            html = "/confyrpapers/" + str(year) + '/' + conf
            entry['paperbreakdown'] =  "<a href='%s'<button>See Papers</button>></a>" %html
            html2 = "/confKWbreakdown/"+ conf + '/' + str(year)
            entry['kwbreakdown'] =  "<a href='%s'<button>Top 10 Keywords</button>></a>" %html2
            html3 = "/jsonconfyrAuthorbd/"+ conf + '/' + str(year)
            entry['authors'] =  "<a href='%s'<button>Authors</button>></a>" %html3
            
            entries.append(entry)
        
        return jsonify(dict(data  = entries))


@App.route("/confbreakdown", methods = ('GET',))
def confbreakdown():
    '''
    Renders getPapersConfYrTable as html
    '''
    return render_template('/conferences/jsonbreakdown.html')
                            
@App.route('/search/<year>/<conf>', methods=('GET',))
def search_params(year, conf):
    '''
    : param year str/int : Year of a conference
    : param conf str : Valid Conference Name (WICSA, ECSA, QoSA)
    : output : Returns a json dictionary of publication 
               year, name, paperIDs, titles
    '''    
    print "publication year", year
    print "conference", conf
    
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
            print (year, conf, 'subgroupfail')
            entry = {'paperID': 'NoConference',
                     'Title': 'NoConference',
                     'Abstract': 'NoConference',
                     }
            mytable = [entry]
            return jsonify(dict(data = mytable))

@App.route('/search')
def search():
    '''
    Renders search_params(year, conf) as html
    '''
    return render_template("/conferences/search.html")

'''
                                                PAPERS BREAKDOWNS AND FUNCTIONS
'''       
def getPapersKWgroup(grouper):
    '''
    : param grouper: parameters to group paper keyword 
                     merged table by (ie. [confName, pubYear])
    : output : Returns two python Pandas DataFrames . 
            merged: PAPER and PAPERKEY merged on paperID
            subgroup : merged grouped by given grouper
    '''
    with sqlite3.connect(mydb) as con:
        sqlcmd = "SELECT paperID, title, confName, pubYear FROM PAPER "
        
        paperdf = pd.read_sql_query(sqlcmd, con)
        
        sqlcmd2 = "SELECT paperID, keyword FROM PAPERKEY "
        kwdf = pd.read_sql_query(sqlcmd2, con)
        kwdf['keyword'] = kwdf['keyword'].apply(lambda word: eval(word))
        
        merged = kwdf.merge(paperdf, on = 'paperID')
        
        subgrp = merged.groupby(grouper)
        
        return merged, subgrp

@App.route("/jsonPaperID/<paperid>", methods = ('GET',))
def getpaperbyID(paperid):
    '''
    : param id integer: PaperID to return 
    : output : Returns python dataframe of the paper with 
    '''
    with sqlite3.connect(mydb) as con:
        sqlcmd = "SELECT paperID, title, confName, pubYear, abstract FROM PAPER WHERE paperID == %d" %int(paperid)
        con.row_factory = dict_factory
        cur = con.cursor()
        cur.execute(sqlcmd)
        entries = cur.fetchall()
    return jsonify(dict(data=entries))

@App.route("/PaperID/<paperid>", methods = ('GET',))
def PaperID(paperid):
    '''
    Renders jsonPaperID(id) as html
    '''
    return render_template('/papers/paperbyID.html', entry = paperid)
    
@App.route("/jsonContentskeys/<conf>/<year>", methods = ('GET',))
def confYrKeywords(year, conf, top = 10):
    '''
    : param conf str : Valid Conference Name (WICSA, ECSA, QoSA)
    : param year str/int : Year of a conference
    : param top int : number of keywords to return, default 10
    : output : Returns a json dictionary of the top 10 keywords 
               for the given conference/year. 
               pie and bar graph representation
    '''    
    print 'Conf: ', conf, 'Year' , year
    grouper = ['confName', 'pubYear']
    m, f = getPapersKWgroup(grouper)
    print 'Got F'
    myentries = []
    try:
        group = (conf, int(year))
        print group
        keywordcts = f.get_group(group).groupby(["keyword"])["keyword"].count()
        print keywordcts
        kwdftop = keywordcts.sort_values(ascending = False).head(top)
        
        resetKW = pd.DataFrame(kwdftop).rename(columns = {'keyword' : 'count'})
        entry = {}
        entry['Group'] = group
        entry['Counts'] = resetKW.reset_index().to_html(classes = 'counts')
        
        image = images.getPieOne(resetKW, group)
        entry['Pie'] = image
        
        resetKW.reset_index(inplace = True)
        image2 = images.getBar(resetKW, 
                                  group, 
                                  xaxis = 'count', yaxis = 'keyword',
                                  orientation = 'h',
                                  ylabel = 'keyword', xlabel = 'Count')
        entry['Bar'] = image2
        
        
        
        myentries.append(entry)
    
    
        return jsonify(dict(data = myentries)) 
    except:
        entry = {
            'Group' :  "No Conference Data",
            'Counts' :  "No Conference Data",
            'Pie' :  "No Conference Data",
            'Bar' :  "No Conference Data"
            }
        myentries.append(entry)
    
    
        return jsonify(dict(data = myentries)) 


@App.route("/confKWbreakdown/<conf>/<year>", methods = ('GET',))
def jsonConfYrKW(conf, year):
    '''
    Renders confYrKeywords() as html
    '''
    return render_template('/keywords/jsonContentsconfyrkw.html', 
                           entry = [conf, year])

@App.route("/papers/keywords", methods = ('GET',))
def getPaperKW():
    '''
    : param NONE
    : output : Returns a json dictionary of 
               paperIDs and their keywords
    '''
    m, data_frame = getPapersKWgroup('paperID')
    entries = []
    for each in data_frame.groups:
        entry = {}
        entry['paperID'] = each
        entry['keywords'] = [key for key in data_frame.get_group(each)['keyword']]
        html2 = "/PaperID/"+ str(each)
        entry['getPaper'] =  "<a href='%s'<button>Paper Information</button>></a>" %html2  
        entries.append(entry)
    return jsonify(dict(data = entries))

@App.route("/paperKWs.html", methods = ('GET',))
def jsonPaperKW():
    '''
    Renders getPaperKW() as html
    '''
    return render_template('/keywords/paperKWs.html')

@App.route('/search_kw')
def search_kw():
    '''
    Renders search_kw_params() as html
    '''
    return render_template("/keywords/search_kw.html")

@App.route('/search_kw/<param>', methods=('GET',))
def search_kw_params(param):
    '''
    : param param str: keyword string to be searched for
    : output : Returns a json dictionary of papers 
               associated to the given keyword
    '''
    print "keyword search: ", param
    
    
    m, f = getPapersKWgroup('keyword')
    
    cts = m.groupby(["keyword"])["keyword"].count().reset_index(name="counts")
   
    ctsmerge = cts.merge(m, on = 'keyword').groupby('keyword')   
    
    try:
        
        print param
        
        subgroup = ctsmerge.get_group(param)
        
        mytable = []
            
        for idx in subgroup.index.get_values():
            print idx
            entry = {}
            entry['paperID'] = subgroup.loc[idx].paperID
            entry['Title'] = subgroup.loc[idx]['title']
            entry['Conference'] = subgroup.loc[idx]['confName']   
            entry['PublicationYear'] = subgroup.loc[idx]['pubYear'] 
            mytable.append(entry)
       
        return jsonify(dict(data = mytable))
    except:
        print (param, 'subgroupfail')
        entry = {'paperID': 'No Keyword Found',
                 'Title': 'No Keyword Found',
                 'Conference': 'No Keyword Found',
                 'PublicationYear': 'No Keyword Found'
                }
        mytable = [entry]
        return jsonify(dict(data = mytable))

@App.route('/seeKWTrend/<kw>', methods=('GET',))
def seeKWTrend(kw, grouper = 'keyword'):
    '''
    : param param str: keyword string to be searched for
    : output : Returns a json dicitonary of a table with 
               the given keyword's associated 
               papers, counts per conference and year,
               and a heatmap represenation
    '''
    print('My keyword: ' , kw)
    m, f = getPapersKWgroup(grouper)
    
    query2 = '"%s" == keyword' %kw
    
    data_frame = m.copy()
    ##could use this if want approx equality
    #data_frame = m[m['keyword'].str.contains(kw)==True]
    data_frame.query(query2, inplace = True)
    new = data_frame.copy()
    
    def findKWTrend(df, kw, KWgrouper = ["pubYear", "confName"]):
        
        df = df.groupby(KWgrouper)['keyword'].count().reset_index(name="counts")
        try:
            image = images.getHeatMap2(df, 
                                       annotation = True, 
                                       filename = "static/Images/test.png")
            html = "/kwHeattrend"
            return df, images.getHeatMap(df, annotation = True), html
        except:
            return df, 'no data', 'error'
        
    
    df, image, html = findKWTrend(new, kw)
    
    myentry = [{'table' : new.to_html(classes = 'counts'),
               'cts' : df.to_html(classes = 'counts'),
               'trend'  : image,
               'url' : "<a href='%s'<button>SeeHeatMap</button>></a>" %html  
               }]
    
    return jsonify(dict(data = myentry))    

@App.route('/kwHeattrend', methods=('GET',))
def seeKWTrendheat():
    '''
    Renders seeKWTrend() as html
    '''
    
    return render_template('keywords/kwHeattrend.html')

@App.route('/seeKWTrends', methods=('GET',))
def seeKWTrends():
    '''
    Renders seeKWTrend() as html
    '''
    
    return render_template('keywords/jsonKWTrends2.html')

@App.route('/seeKWTop', methods=('GET',))
def seeKWTop(top = 20):
    '''
    : param top int: number of top keywords to return, default 20
    : output : Returns a json dicitonary of the frequency of the top 
                keywords over all years and a heatmap
    '''
    m, f = getPapersKWgroup('keyword')
    
    topWds = f.count().sort_values(by = 'confName', 
                                   ascending = False)[:top]
    
    mTop = m[m['keyword'].isin(topWds.index)]
    
    mTop['counts'] = mTop.groupby(['confName', 'pubYear', 'keyword'])['keyword'].transform('count')
    
    image = images.getHeatMap2(mTop, indexCol='keyword', 
                               cols = ['confName', 'pubYear'], 
                               vals = 'counts', 
                               filename = 'static/Images/topheat.png')
    
    html = "/topheat"
    topWds.reset_index(inplace = True)
    topWds.rename(columns = {'confName' : 'OverallCount'}, 
                  inplace = True)
    cts = topWds[['keyword', 'OverallCount']]
    
    
    
    return jsonify(dict(data = 
                        [{'Top' : cts.to_html(classes = 'counts'),
                       'HeatMap' : "<a href='%s'<button>SeeHeatMap</button>></a>" %html}]
                       )
                    )

@App.route('/topKW', methods=('GET',))
def topKW():
    '''
    Renders seeKWTop() as html
    '''
    return render_template('keywords/topKW.html')

@App.route('/topheat', methods=('GET',))
def topheat():
    '''
    Renders getBasicAffiliationCount() as html
    '''
    
    return render_template('keywords/topheat.html')

@App.route('/KWcloud', methods=('GET',))
def KWcloud():
    '''
    Renders KWs word cloud in html 
    - creates and SAVES a newimage eachtime
    '''
    wordCloud =  wcg.cloud('kw', 
                           outputFile = "static/Images/kwCloud.png")
    return render_template('keywords/wordcloudrender.html')


@App.route('/create_KWCloudGroup/<grouper>/<grouptype>', methods=('GET',))
def create_KWCloudGroup(grouper, grouptype):
    if grouper == 'pubYear':
        grouptype = int(grouptype)
        
    wordCloud = wcg.cloud(cloudtext = 'kw',
                    grouper = grouper, 
                    group = grouptype, 
                    outputFile = 'static/Images/kwGroupedCloud.png',
                    grouped = True
                    )
    print(grouper, grouptype)
    
    return render_template('keywords/wordcloudGrouprender.html', 
                           entry = grouptype)

@App.route('/wordCloudSearcher2')
def directionstoSearchCloud():
    return render_template("keywords/directions.html")

@App.route('/create_KWCloudGroup2/<grouptype>', methods=('GET',))
def create_KWCloudGroup2(grouptype):

    try:
        image = wcg.cloud2(cloudtext = 'kw',
                    grouper = 'confName', 
                    group = grouptype,
                    grouped = True
                    )
        print(image)
        return jsonify(dict(data = [{'KWCloud'  : image}]))
    
    except:
        image = 'static/Images/colorBars.png'
        print('error')
        return jsonify(dict(data = [{'KWCloud'  : image}]))

@App.route('/wordCloudSearcher3', methods=('GET',))
def wordCloudSearcher3():
    '''
    Renders create_KWCloudGroup2() as html
    '''
    
    return render_template('keywords/wordCloudSearcher3.html')
        
def getAffiliation():
    
    with sqlite3.connect(mydb) as con:
        sqlcmd = "SELECT paperID, affiliation, confName, pubYear FROM PAPER "
        
        paperdf = pd.read_sql_query(sqlcmd, con)
        
        
        return paperdf
'''
                                                AFFILIATION FUNCTIONS
''' 

@App.route('/searchAffiliation/<term>', methods=('GET',))
def searchAffiliation(term):
    '''
    : param term: term by which to search Affiliations 
                 (ie country, number, abbreviation)
    : output : json dictionary of paperID, affilation, 
                  and link to the PaperID Info 
    '''
   
    with sqlite3.connect(mydb) as con:
        sqlcmd = "SELECT paperID, affiliation, confName, pubYear FROM PAPER "
        
        paperdf = pd.read_sql_query(sqlcmd, con)
        
        datadf = paperdf[paperdf['affiliation'].str.contains(term or term.lower())==True]
        
        mytable = []
        for idx in datadf.index.get_values():
            entry = {}
            entry['paperID'] = datadf.loc[idx]['paperID']
            entry['affiliation'] = datadf.loc[idx]['affiliation']
            html2 = "/PaperID/"+ str(datadf.loc[idx]['paperID'])
            entry['getPaper'] =  "<a href='%s'<button>Paper Information</button>></a>" %html2  
            
            mytable.append(entry)
        
        return jsonify(dict(data = mytable))

@App.route('/seeAffil', methods=('GET',))
def seeAffil():
    '''
    Renders searchAffiliation(term) as html
    '''
    return render_template('papers/seeAffil.html')

def getBasicAffiliationCount():
    '''
    : param NONE:
    : output : Dictionary of the found countries,their counts, barchart
    '''
    from pycountry import countries 
    with sqlite3.connect(mydb) as con:
        sqlcmd = "SELECT affiliation FROM PAPER "
        
        affildf = pd.read_sql_query(sqlcmd, con)
        countries = [country.name for country in countries]
        
        counts = {}
        for c in countries:
            count = len(affildf[affildf['affiliation'].str.contains(c or c.lower())==True])
            if count > 0:
                counts[c] = count
        image = images.getaffilbar(xaxis = counts.keys(), 
                                   yaxis = counts.values())
        
    
        
        return counts, image
    
@App.route('/seeCountries', methods=('GET',))
def seeCountries():
    '''
    Renders getBasicAffiliationCount() as html
    '''
    seeCountries, image = getBasicAffiliationCount()
    
    return render_template('papers/seeCountries.html')

@App.route('/getCountryCounts', methods=('GET',))
def getCountryCounts():
    '''
    : param : NONE
    : output : json dictionary of the affiliation count and country 
        (dictionary output of  getBasicAffiliationCount())
    '''
    cts, img = getBasicAffiliationCount()
    datadic=[]
    for i, (k, v) in enumerate(cts.iteritems()):
        datadic.append({'country' : k, 'count' : v})
    
    return jsonify(dict(data = datadic))

@App.route('/countryCts', methods=('GET',))
def seeCountryCounts():
    '''
    Renders  getCountryCounts() as html
    '''
    return render_template('papers/seeCountryCounts.html')

def countryGr():
    '''
    : param : NONE
    : output : pandas DataFrame count and 
               country grouped by Conferences
    '''
    from pycountry import countries 
    with sqlite3.connect(mydb) as con:
        sqlcmd = "SELECT affiliation, confName FROM PAPER"
        
        affildf = pd.read_sql_query(sqlcmd, con)
        
        gr = affildf.groupby('confName')
        countries = [country.name for country in countries]
        grouped = {}
        for group in gr.groups.keys():
            temp = gr.get_group(group)
            counted = {}
            for c in countries:
                count = len(temp[temp['affiliation'].str.contains(c)==True])
                if count > 0 :
                    counted[c] = count
            grouped[group] = counted
        
        return pd.DataFrame.from_dict(grouped)
    
@App.route('/seeCountriesGR', methods=('GET',))
def seeCountriesGR():
    '''
    Renders countryGr() as a Bubble Chart and as html
    '''
    image = images.createSpot(countryGr())
    
    return render_template('papers/seeCountriesGR.html')

@App.route('/seeCountriesAreaPlot', methods=('GET',))
def seeCountriesAreaPlot():
    '''
    Renders countryGr() as an AreaPlot and as html
    '''
    image = images.areaPlot(countryGr(), 
                            xlabel = 'Countries', 
                            ylabel = 'Counts', 
                            filename = 'static/Images/countryAP.png')
    
    return render_template('papers/seeCountriesAreaPlot.html')



'''
                                                AUTHORS BREAKDOWNS AND FUNCTIONS
''' 
def getAuthorsTotal():
    with sqlite3.connect(mydb) as con:
        sqlcmd = "SELECT authorName FROM PAPERAUTHOR "
        
        return pd.read_sql_query(sqlcmd, con)
    
    
def AuthoredPapersDF(boolean):
    '''
    : param boolean: control flow boolean
    : output : Returns a python Pandas DataFrane of total 
               database of paperIDs merged to authors 
    '''
    if boolean == 'start':
    
        with sqlite3.connect(mydb) as con:
            sqlcmd = "SELECT * FROM PAPERAUTHOR"
        
            papaudf = pd.read_sql_query(sqlcmd, con)
        
            sqlcmd2 = "SELECT paperID, title, confName, pubYear FROM PAPER"
        
            pap  = pd.read_sql_query(sqlcmd2, con)
        
            merged = papaudf.merge(pap, on =  'paperID')
            merged['counts'] = merged.groupby(['authorName'])['authorName'].transform('count')
        
            return merged.sort_values(by = ['counts','authorName'], ascending = False)
            
            

@App.route('/AuthoredPapers', methods=('GET',))
def AuthoredPapers():
    '''
    : param NONE:
    : output : Returns a json dictionary of Authors and their 
               associated papers by conference and year.
               The count is the total number of papers the author 
               has been ascribed over the entirety of the database 
    '''
    ap = AuthoredPapersDF('start')
    entries = []
    for row in ap.as_matrix():
        entry = {key: value for (key, value) in zip(ap.columns, row)}
        entries.append(entry)
        
    return jsonify(dict(data = entries))

@App.route('/authors/authoredpapers', methods=('GET',))
def authoredpapers():
    '''
    Renders AuthoredPapers() as html
    '''
    return render_template('authors/authoredpapers.html')
    

@App.route('/getauthorsbyID/<paperID>', methods=('GET',))
def getauthorsbyID(paperID):
    '''
        : param paperID int: integer corresponding to the paperID
        : output : Given a valid paperID returns a json dictionary 
                   of authors ascribed to the given paper, 
                   Though redundant, paper title, conference, 
                   year is also returned.
                   The count is the total number of papers the author has 
                   been ascribed over the entirety of the database
    '''
    print paperID
    ap = AuthoredPapersDF('start')
    query = 'paperID == %d' %int(paperID)
    
    ap = ap.query(query)
    entries = []
    
    for row in ap.as_matrix():
        entry = {key: value for (key, value) in zip(ap.columns, row)}
        entries.append(entry)
    return jsonify(dict(data = entries))

@App.route('/authors/seeAuthorsID', methods=('GET',))
def seeAuthorsID():
    '''
    Renders getAuthors() as html
    '''
    return render_template('authors/seeAuthorsID.html')

@App.route('/getauthorsbyname/<name>', methods=('GET',))
def getauthorsbyname(name):
    '''
        : param name str: string corresponding to an authors name. 
                          SPACE SENSITIVE
        : output : Given a valid author name returns a json dictionary of 
                          papers ascribed to the author, 
                          the conference, title, and year.
    '''
    print name
    ap = AuthoredPapersDF('start')
    
    #for author with name containing the name, thus only have to enter the last name.
    ap = ap[ap['authorName'].str.contains(name)==True]
    entries = []
    
    for row in ap.as_matrix():
        entry = {key: value for (key, value) in zip(ap.columns, row)}
        entries.append(entry)
    return jsonify(dict(data = entries))

@App.route('/authors/seeAuthorsName', methods=('GET',))
def seeAuthorsName():
    '''
    Renders getauthorsbyname() as html
    '''
    return render_template('authors/seeAuthorsName.html')

@App.route('/confyrAuthor', methods=('GET',))
def confYrAuthor():
    '''
        : param NONE
        : output : Returns a json dictionary containing Papers,
                   Authors merged grouped by Conference and Year. 
                   Used for inspection
    '''
    grouper = ['confName', 'pubYear']
    f = AuthoredPapersDF('start')
    grouper = ['confName', 'pubYear']
    testgroup = f.groupby(grouper)
    
    myentries = []
    for group in testgroup.groups.keys():
        authorcts = testgroup.get_group((group)).groupby(["authorName"])["authorName"].count()
        
        resetAU = pd.DataFrame(authorcts).rename(columns = {'authorName' : 'IndivCt'})
        resetAU.reset_index(inplace = True)
        
        mer = pd.merge(resetAU, testgroup.get_group((group)))
            
        entry = {}
        entry['Group'] = group
        entry['AuthoredPapers'] = mer.to_html()
        
        
        myentries.append(entry)
    
    return jsonify(dict(data = myentries))

@App.route('/authors/seeAuthorsCY', methods=('GET',))
def seeAuthorsCY():
    '''
    Renders confYrAuthor() as html
    '''
    return render_template('authors/seeAuthorsCY.html')

@App.route('/confyrAuthor_bd/<conf>/<year>', methods=('GET',))
def confYrAuthor2(conf, year):
    '''
        : param conf str : Valid Conference Name (WICSA, ECSA, QoSA)
        : param year str/int : Year of a conference within range of 
                database 2004 - 2014
        : output : Returns a json dictionary containing Authors, paperIds, 
                titles of papers published in given conf/year
                AuthorYrCount is the total number of papers ascribd to a given 
                author in the given conf/year
    '''
    grouper = ['confName', 'pubYear']
    f = AuthoredPapersDF('start')
    grouper = ['confName', 'pubYear']
    group = f.groupby(grouper)
    
    try:
        print (conf, year)
        subgroup =  group.get_group((conf, int(year)))
                                  
        print ('subgroupmade')
        cts = subgroup.groupby(["authorName"])["authorName"].count()
        
            
        resetAU = pd.DataFrame(cts).rename(columns = {'authorName' : 'IndivCt'})
        resetAU.reset_index(inplace = True)
        
        merged = pd.merge(resetAU, subgroup)

        mytable = []
        for idx in merged.index.get_values():
            entry = {}
            entry['Author'] = merged.loc[idx]['authorName']
            entry['paperID'] = merged.loc[idx]['paperID']
            entry['Title'] = merged.loc[idx]['title']
            entry['AuthorYrCount'] = merged.loc[idx]['IndivCt']    
            
            mytable.append(entry)
        
        return jsonify(dict(data = mytable))
    
    except:
        print('Conference Year error')
        mytable = {entry['Author'] : 'No Conference Data',
                   entry['paperID'] : 'No Conference Data',
                   entry['Title'] : 'No Conference Data',
                   entry['AuthorYrCount'] : 'No Conference Data'
                   }
        return jsonify(dict(data = mytable))

@App.route("/jsonconfyrAuthorbd/<conf>/<year>", methods = ('GET',))
def jsonconfyrAuthorbd(conf, year):
    '''
    Renders confYrAuthor2() as html
    '''
    
    return render_template('authors/seeAuthorsCYbd.html', entry = [conf, year]) 

def getAuthorTop20(top = 20, column = 'authorName'):
    
    with sqlite3.connect(mydb) as con:
        
        sqlcmd = "SELECT * FROM PAPERAUTHOR"
        papaudf = pd.read_sql_query(sqlcmd, con)
        
        sqlcmd2 = "SELECT paperID, confName FROM PAPER"
        pap  = pd.read_sql_query(sqlcmd2, con)
        
        merged = papaudf.merge(pap, on =  'paperID')
        merged['counts'] = merged.groupby([column])[column].transform('count')
        
        ap = merged.sort_values(by = ['counts',column], 
                                ascending = False).drop_duplicates(column)[:20]
        
        temp = merged.groupby('confName')
        selection = np.array(ap[column])
        
        return temp, selection
    
def getGrCts(data_frame, selection, column):
    
    grouped = {}
    for group in data_frame.groups.keys():
        temp = data_frame.get_group(group)
        counted = {}
        for au in selection:
            count = len(temp[temp[column].str.contains(au)==True])
            if count > 0 :
                counted[au] = count
            grouped[group] = counted
    return pd.DataFrame.from_dict(grouped)

@App.route('/auCloud', methods=('GET',))
def auCloud():
    '''
    Renders Authors word cloud in html - 
    creates and SAVES a newimage eachtime
    '''
    wordCloud =  wcg.cloud('au', outputFile = "static/Images/auCloud.png")
    return render_template('authors/wordcloudrenderer_au.html')

@App.route('/seeAuthorsSpot', methods=('GET',))
def seeAuthorsSpot():
    '''
    Renders countryGr() as an Bubble and as html
    '''
    topauthors, selection = getAuthorTop20(top = 20)
    groupedAu = getGrCts(topauthors, selection, column = 'authorName')
    image = images.createSpot(groupedAu, 
                              xlabel = 'Author', 
                              filename = 'static/Images/authorBubble.png')
    
    return render_template('authors/seeAuthorsSpot.html')

@App.route('/seeAuthorsArea', methods=('GET',))
def seeAuthorsArea():
    '''
    Renders countryGr() as an AreaPlot and as html
    '''
    topauthors, selection = getAuthorTop20(top = 20)
    groupedAu = getGrCts(topauthors, selection, column = 'authorName')
    image = images.areaPlot(groupedAu, 
                            xlabel = 'Authors', 
                            ylabel = 'counts', 
                            filename = 'static/Images/authorAP.png')
    
    
    return render_template('authors/seeAuthorsArea.html')

@App.route('/show_tables', methods=('GET',))
def show_tables():
    data =  getAffiliation()
    
    data.index.name=None
    ECSA = data.loc[data.confName=='ECSA']
    WICSA = data.loc[data.confName=='WICSA']
    QoSA = data.loc[data.confName == 'QoSA']
    return render_template('view.html',tables=[ECSA.to_html(classes='ECSA'),
                                               WICSA.to_html(classes='WICSA'), 
                                               QoSA.to_html(classes='QoSA')],
    titles = ['na', 'ECSA', 'WICSA', 'QoSA'])

@App.route('/show_tables2')
def analysis():
    data =  getAffiliation()
    return render_template("show2.html", name='tables', data=data)

import RESTful

def openJfile(jfile):
    '''
        : param jfile str/unicode : json file name (located in static folder/data)
        : output : Opens and returns json file as pandas dataframe
    '''
    SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
    json_url = os.path.join(SITE_ROOT, "static/data", str(jfile))
    
    return json_url

@App.route('/queries', methods=['GET'])
def myquery():
    e = RESTful.retrievals(mydb, 'CONFERENCES', 'confName', 'confID', 'confID', 3)
    
    return jsonify(dict(data=e))

@App.route('/seeJfile/<jfile>', methods=['GET'])
def seeJsonDF(jfile):
    '''
        : param jfile str/unicode : json file name (located in static folder/data)
        : output : Opens and renders json file as pandas dataframe in html format
    '''
    f = openJfile(jfile)
    
    return RESTful.jsonDF(f).to_html()

@App.route('/insertJfile/<jfile>', methods=['GET'])
def insertJFiletoDB(jfile):
    '''
        : param jfile str/unicode : json file name (located in static folder/data)
        : output : Opens and renders json file as pandas dataframe in html format
    '''
    f = openJfile(jfile)
    
    return RESTful.entryintotables(mydb, f).to_html()

@App.route('/delete/<table>/<cn>/<param>', methods=['GET'])
def deleteRow(table, cn, param):
    '''
        : param  db str : Database name to connect to
        : param  table str : Table Name to delete from
        : param  cn str : column name being used for deletion comparason
        : param  param int/str : value to lok up and delete row
    '''
    
    result = 'ERROR IN STR DELETION, look at column name or str value'
    if str(param).isdigit():
        try:          
            result = RESTful.deleteRowPK(mydb, table, cn, int(param))   
        except:
            pass
    else:
        try:
            result = RESTful.deleteRowOTHER(mydb, table, cn,  param)
        except:
            pass
    return result

@App.route('/deletePaper/<paperID>', methods=['GET'])
def deletePaperfromDB(paperID):
    '''Delete  a paper from the database, (composites, CASCADE)
        : param  paperID int/str : value to look up and delete record from database
        : output : deleted paper as dataframe
    '''
    
    result = RESTful.deleteFromDB_PaperID(int(paperID), db = mydb)
    #return render_template('view.html',tables=[result.to_html(classes='ECSA')], titles = 'deleted)
    #return result.to_html()


    return render_template('view.html',tables=[ result.to_html(classes='QoSA')], titles = ['na', 'DELETED'])
if __name__ == '__main__':
   
    App.debug=True
    App.run()
