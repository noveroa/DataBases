#!/usr/bin/env python

import flask
import os
import sqlite3
import pandas as pd
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
from flask import abort,  jsonify

import images as images
images = reload(images)
import wordcloud_generator as wcg
wcg = reload(wcg)

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
    """ Displays the page about author
    """
    return flask.render_template('extras/aboutMe.html')

@App.route('/welcome/<name>/')
def welcome(name):
    """ Displays the welcome screen.
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
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


'''
                                                TOTAL TABLES
''' 
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
    return render_template('/totaltables/jsonContents.html')

'''
                                        CONFERENCE BREAKDOWNS AND FUNCTIONS - BY YEAR
'''


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
            
            subDF.reset_index(inplace = True)
            image2 = images.getBar(subDF, 
                                    conf, 
                                    xaxis = 'year', yaxis = 'Conf', 
                                    orientation = "v",
                                    ylabel = 'Count', xlabel = 'Publication Year')
            
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

@App.route("/jsonconfyrbreakdown", methods=('GET',))
def getPapersConfYrTable():
    with sqlite3.connect(mydb) as con:
        sqlcmd = "SELECT pubYear, confName, paperID, title, abstract FROM PAPER"
        PAPdf = pd.read_sql_query(sqlcmd, con)
    
        group = PAPdf.groupby(['pubYear', 'confName'], axis = 0)
        entries = []
        for year, conf in group.groups.keys():
            entry = {}
            entry['conference'] = conf
            entry['year'] = year
            
            html = "http://127.0.0.1:5000/confyrpapers/" + str(year) + '/' + conf
            entry['paperbreakdown'] =  "<a href='%s'<button>See Papers</button>></a>" %html
            html2 = "http://127.0.0.1:5000/confKWbreakdown/"+ conf + '/' + str(year)
            entry['kwbreakdown'] =  "<a href='%s'<button>Top 10 Keywords</button>></a>" %html2
            html3 = "http://127.0.0.1:5000/jsonconfyrAuthorbd/"+ conf + '/' + str(year)
            entry['authors'] =  "<a href='%s'<button>Authors</button>></a>" %html3
            
            entries.append(entry)
        
        return jsonify(dict(data  = entries))

@App.route("/confyrpapers/<year>/<conf>", methods = ('GET',))
def jsonConfYrPaper(year, conf):
    '''Display the papers from a given year and conference table'''
    
    return render_template('/conferences/ConfYrPaper.html', entry = [year, conf])

@App.route("/contentsconf", methods = ('GET',))
def jsonContentsconf():
    '''Display the total table'''
    
    return render_template('/conferences/jsonContentsconf.html')

@App.route("/confbreakdown", methods = ('GET',))
def confbreakdown():
    '''Display the total table'''
    
    return render_template('/conferences/jsonbreakdown.html')

@App.route('/search')
def search():
    return render_template("/conferences/search.html")

@App.route('/search/<param1>/<param2>', methods=('GET',))
def search_params(param1, param2):
    print "param1", param1
    print "param2", param2
    
    with sqlite3.connect(mydb) as con:
        sqlcmd = "SELECT pubYear, confName, paperID, title, abstract FROM PAPER"
        PAPdf = pd.read_sql_query(sqlcmd, con)
    
        group = PAPdf.groupby(['pubYear', 'confName'], axis = 0)
       
        try:
            print (param1, param2)
            subgroup =  group.get_group((int(param1), param2))
            print (param1, param2, 'subgroupmade')
            
                                     
        
            mytable = []
            
            for idx in subgroup.index.get_values():
                entry = {}
                entry['paperID'] = subgroup.loc[idx]['paperID']
                entry['Title'] = subgroup.loc[idx]['title']
                entry['Abstract'] = subgroup.loc[idx]['abstract']    
                mytable.append(entry)
       
            return jsonify( dict(data = mytable))
        except:
            print (param1, param2, 'subgroupfail')
            entry = {'paperID': 'NoConference',
                     'Title': 'NoConference',
                     'Abstract': 'NoConference',
                     }
            mytable = [entry]
            return jsonify(dict(data = mytable))

'''
                                                PAPERS BREAKDOWNS AND FUNCTIONS
'''       
def getPapersKWgroup(grouper):
    '''
    : param grouper: parameters to group paper keyword merged table by (ie. [confName, pubYear])
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
    : param year str/int : Year of a conference within range of database 2004 - 2014
    : param top int : number of keywords to return, default 10
    : output : Returns a json dictionary of the top 10 keywords for the given conference/year. 
                And a bie and bar graph representation
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
        entry['Counts'] = resetKW.to_html()
        
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
    return render_template('/keywords/jsonContentsconfyrkw.html', entry = [conf, year])

@App.route("/papers/keywords", methods = ('GET',))    
def getPaperKW():
    '''
    : param NONE
    : output : Returns a json dictionary of paperIDs and their keywords
    '''
    m, data_frame = getPapersKWgroup('paperID')
    entries = []
    for each in data_frame.groups:
        entry = {}
        entry['paperID'] = each
        entry['keywords'] = [key for key in data_frame.get_group(each)['keyword']]
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
    : output : Returns a json dictionary of papers associated to the given keyword
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
    : output : Returns a json dicitonary of a table with the given keyword's associated 
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
    
    def findKWTrend(df, KWgrouper = ["pubYear", "confName"]):
        #labels = {'ECSA' : 0,
                  #'QoSA' : 1,
                  #'WICSA' : 2}
        df = df.groupby(KWgrouper)['keyword'].count().reset_index(name="counts")
        #df['confCode'] = df.confName.apply(lambda name: labels[name])
        try:
            return df, images.getHeatMap(df, annotation = True)
        except:
            return df, 'no data'
        
    
    df, image = findKWTrend(new)
    
    myentry = [{'table' : new.to_html(),
               'cts' : df.to_html(),
               'trend'  : image
               }]
    
    return jsonify(dict(data = myentry))    

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
    
    topWds = f.count().sort_values(by = 'confName', ascending = False)[:top]
    
    mTop = m[m['keyword'].isin(topWds.index)]
    
    mTop['counts'] = mTop.groupby(['confName', 'pubYear', 'keyword'])['keyword'].transform('count')
    
    image = images.getHeatMap(mTop, indexCol='keyword', 
                              cols = ['confName', 'pubYear'], vals = 'counts')
    
    topWds.reset_index(inplace = True)
    topWds.rename(columns = {'confName' : 'OverallCount'}, inplace = True)
    cts = topWds[['keyword', 'OverallCount']]
    
    
    
    return jsonify(dict(data = 
                        [{'Top' : cts.to_html(),
                       'HeatMap' : image}]
                       )
                    )

@App.route('/topKW', methods=('GET',))
def topKW():
    '''
    Renders seeKWTop() as html
    '''
    return render_template('keywords/topKW.html')


#@App.route('/dictKWcloud', methods=('GET',))
#def dictKWcloud():
    #'''
    #Renders KWs word cloud in html
    #'''
    #get the word cloud!
    #wordCloud =  wcg.KWcloud2()
    #return jsonify(dict(data = 
    #                    [{'image' : wordCloud}]
    #                   )
    #                )
#
#@App.route('/KWcloud2', methods=('GET',))
#def KWcloud2():
#    '''
#    #Renders KWs word cloud in html
#    '''
#    
#    return render_template('/wordcloudtest2.html')
#'''
@App.route('/KWcloud', methods=('GET',))
def KWcloud():
    '''
    Renders KWs word cloud in html - creates and SAVES a newimage eachtime
    '''
    wordCloud =  wcg.KWcloud("static/Images/pawtest2.png")
    return render_template('keywords/wordcloudtest.html')

def getAffiliation():
    
    with sqlite3.connect(mydb.db) as con:
        sqlcmd = "SELECT paperID, affiliation, confName, pubYear FROM PAPER "
        
        paperdf = pd.read_sql_query(sqlcmd, con)
        
        
        return paperdf
'''
                                                AFFILIATION FUNCTIONS
''' 

@App.route('/searchAffiliation/<term>', methods=('GET',))
def searchAffiliation(term):
    '''
    : param term: term by which to search Affiliations (ie country, number, abbreviation)
    : output : json dictionary of paperID, affilation, and link to the PaperID Info 
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
            html2 = "http://127.0.0.1:5000/PaperID/"+ str(datadf.loc[idx]['paperID'])
            entry['getPaper'] =  "<a href='%s'<button>getPaper</button>></a>" %html2  
            
            mytable.append(entry)
        
        return jsonify(dict(data = mytable))

@App.route('/seeAffil', methods=('GET',))
def seeAffil():
    '''
    Renders searchAffiliation(country) as html
    '''
    return render_template('papers/seeAffil.html')

'''
                                                AUTHORS BREAKDOWNS AND FUNCTIONS
''' 

def AuthoredPapersDF(boolean):
    '''
    : param boolean: control flow boolean
    : output : Returns a python Pandas DataFrane of total database of paperIDs merged to authors 
    '''
    if boolean == 'start':
    
        with sqlite3.connect(mydb) as con:
            sqlcmd = "SELECT * FROM PAPERAUTHOR"
        
            papaudf = pd.read_sql_query(sqlcmd, con)
        
            sqlcmd2 = "SELECT paperID,title,confName, pubYear FROM PAPER"
        
            pap  = pd.read_sql_query(sqlcmd2, con)
        
            merged = papaudf.merge(pap, on =  'paperID')
            merged['counts'] = merged.groupby(['authorName'])['authorName'].transform('count')
        
            return merged.sort_values(by = ['counts','authorName'], ascending = False)
            
            

@App.route('/AuthoredPapers', methods=('GET',))
def AuthoredPapers():
    '''
    : param NONE:
    : output : Returns a json dictionary of Authors and their associated papers by conference and year.
               The count is the total number of papers the author has been ascribed over the entirety of the database 
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
        : output : Given a valid paperID returns a json dictionary of authors ascribed to the given paper, 
                   Though redundant, paper title, conference, year is also returned.
                   The count is the total number of papers the author has been ascribed over the entirety of the database
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
        : param name str: string corresponding to an authors name. SPACE SENSITIVE
        : output : Given a valid author name returns a json dictionary of papers ascribed to the author, 
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
        : output : Returns a json dictionary containing Papers,Authors merged grouped by Conference and Year. 
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
        : param year str/int : Year of a conference within range of database 2004 - 2014
        : output : Returns a json dictionary containing Authors, paperIds, titles of papers published in given conf/year
                    AuuthorYrCount is the total number of papers ascribd to a given author in the given conf/year
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

if __name__ == '__main__':
   
    App.debug=True
    App.run()
    
