#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import sqlite3
import pandas as pd

''' Some Starting Point Scripts for creating a SQL DB based on the 
    Abstracts Data parsed into a DataFrame'''

DEFAULTDB = 'Abstracts_DB.db'
DEFAULTHDF = '../DataBaseParsing/DFstore32.h5'
def parseDataFrame(hdffile = DEFAULTHDF, 
                   key = 'df'):
    '''Parse a h5 file into readble rows for a Abstracts Table.
       : param hdffile : str. directory location of the h5 file
               default : '../DataBaseParsing/DFstore.h5'
       : param key : str. h5 key for the DF with data.
               default : 'df'
    '''
    
    totalDF = pd.read_hdf(hdffile, key)
    print(totalDF.shape)
    
    rows = []
    for x in totalDF.itertuples():
        rows.extend([x])
        
    return rows
    

def sqlCMDToPD(table, 
               db = DEFAULTDB):
    '''Take a sql db and return as a readable pandas DataFrame
       : param db : str. Name of db. (ie. 'Abstracts.db'
       : param sqlcmd : str. Sqlite3 cmd to execute. 
               default: "SELECT * FROM Abstracts" 
                           > select all from Abstracts table
    '''
    
    #connect to a db
    with sqlite3.connect(db) as con:
        
        #run command
        sqlcmd = "SELECT * FROM '%s'" %table
        df = pd.read_sql_query(sqlcmd, con)
        
        # Check resulting pandas DF shape
        print df.shape
        
        return df



def createTOTALTable(entries, 
                      db = DEFAULTDB,
                      table = 'ABSTRACTSTOTAL'):
    '''Add entries to the given db
       : param entries : list of tuples 
       : param db : str. Name of db. (ie. 'Abstracts.db'
       : param table : str. Name of Table to create or insert.
           : [(1, 'Audi', 'A', 'B', 'C', 'D', 'E', 'F', 'G'),
              (2, 'Passat', 'H', 'I', 'C', 'D', 'J', 'K', 'Z')
              ]
       
      : output : Pandas DataFrame for inspection
      
    '''
    with sqlite3.connect(db) as con:
        cur = con.cursor() 
        #drops the Abstracts table if it exist in db already
        cur.execute("DROP TABLE IF EXISTS " + table)
        #and recreates it
        cur.execute("CREATE TABLE " + table +
                    "(\
                    ID INT, \
                    Abstract TEXT, \
                    'Author affiliation' TEXT, \
                    Authors TEXT, \
                    Conf TEXT, \
                    Title TEXT, \
                    terms TEXT,\
                    year INT\
                    )");

        cur.executemany("INSERT INTO " +  table +  
                        " VALUES(?,?,?,?,?,?,?,?)", entries )
        
        sql = "SELECT * FROM " + table
        df = pd.read_sql_query(sql, con)
        
        #return table as Pandas DataFrame for inspection
        return df  

def createConfTable(entries, 
                    db = DEFAULTDB, 
                    table = 'CONFERENCES' ):
    
    ''' Creating the CONFERENCES Table with AutoIncremented PRIMARY Key as ConfID
         : param entries : list of str. Unique Conference Names, 
             : default the result of groupby on main table
         : param db : str. Name of db. (ie. 'Abstracts.db')
             : default 'TestAbstracts.db'
         : param table : str. Name of Table to create or insert.
             : default : CONFERENCES
         
         : output : Pandas DataFrame as output for inspection
         '''
    
    with sqlite3.connect(db) as con:
        print ("Opened %s database successfully" %db); 
        cur = con.cursor() 
        #drops the Abstracts table if it exist in db already
        cur.execute("DROP TABLE IF EXISTS " + table)
        #and recreates it
        cur.execute("CREATE TABLE " + table + "(\
        confID INTEGER PRIMARY KEY AUTOINCREMENT, \
        confName TEXT NOT NULL)") 
        
        for conference in entries:
            name = conference
            cur.execute("INSERT INTO " + table + 
                        "(confName)\
                        VALUES ('%s')" %name);
            print 'Entry %s added' %name
        
        print "Records created successfully";
        
        #return table as Pandas DataFrame for inspection
        sql = "SELECT * FROM " + table
        df = pd.read_sql_query(sql, con)
        return df
        
def createPublicationsTable(entries, 
                            db = DEFAULTDB, 
                            table = 'PUBLICATIONS', 
                            foreignKey = 'CONFERENCES'):
    
    ''' Creating the Publications Table with 
                pubID as AUTOINCREMENTED PRIMARY KEY, 
                confName with FOREIGN KEY reference
            
         : param entries : list of tuples: 
             (Conference Name: Year of Publication)
             : default the result of groupby on main table
         : param db : str. Name of db. (ie. 'Abstracts.db')
             : default 'TestAbstracts.db'
         : param table : str. Name of Table to create or insert.
         
         : output : Pandas DataFrame as output for inspection
           
    '''
    with sqlite3.connect(db) as con:
        print ("Opened %s database successfully" %db);
        cur = con.cursor() 
        #drops the Abstracts table if it exist in db already
        cur.execute("DROP TABLE IF EXISTS " + table)
        print ('table dropped')
        
        
        #create the table
        cur.execute("CREATE TABLE " + table + 
                    "(pubID INTEGER PRIMARY KEY AUTOINCREMENT, \
                    year INT, \
                    confName TEXT NOT NULL, \
                    FOREIGN KEY(confName) REFERENCES '%s'(confID))" % foreignKey); 
        
        print('Created %s table' %table);
        
        #insert into the table
        for confName, year in entries:
            #print('Conference %s' %confName)
            cur.execute("INSERT INTO " + table + 
                        "(year, confName) \
                        VALUES ('%s','%s')" %(year, confName))
            #print ('Entry %d added' %year)
        
        print "Records created successfully";
        
        sql = "SELECT * FROM " + table
        df = pd.read_sql_query(sql, con)
        
        #return table as Pandas DataFrame for inspection
        return df           

    
def createAbstractsTable(entries ,
                         db = DEFAULTDB,
                         table = 'ABSTRACTS',
                         foreignKey = 'PUBLICATIONS'):
    
    ''' Creating the Publications Table with 
                pubID as AUTOINCREMENTED PRIMARY KEY, 
                pubYear as FOREIGN KEY reference to year in PUBLICATIONS
                conf with FOREIGN KEY reference to confName in PUBLICATIONS
                
            
         : param entries : the ABSTRACTSTOTAL table as a matrix 
         : param db : str. Name of db. (ie. 'Abstracts.db')
             : default 'TestAbstracts.db'
         : param table : str. Name of Table to create or insert.
         : param foreignKey : str. 
         
         : output : Pandas DataFrame as output for inspection
           
    '''
    with sqlite3.connect(db) as con:
        print ("Opened %s database successfully" %db);
        cur = con.cursor() 
        #drops the Abstracts table if it exist in db already
        cur.execute("DROP TABLE IF EXISTS " + table)
        print ('table dropped')
        
        
        #create the table
        cur.execute("CREATE TABLE " + table + 
                    "(pubID INTEGER PRIMARY KEY AUTOINCREMENT, \
                    pubYear INT NOT NULL, \
                    conf TEXT NOT NULL, \
                    abstract TEXT, \
                    title TEXT, \
                    FOREIGN KEY(pubYear) REFERENCES '%s', \
                    FOREIGN KEY(conf) REFERENCES '%s'(confName))" % (foreignKey, foreignKey)); ##authors ids?
        
        print('Created %s table' %table);
        
        #insert into the table
        for idx, abstr, aFil, aus, conf,title,terms, year in entries:
            
            cur.execute("INSERT INTO " + table + 
                        "(pubYear, conf, abstract, title) \
                        VALUES ('%d','%s', '%s', '%s')" 
                        %(year, conf, abstr, title))
        
        print "Records created successfully";
        
        sql = "SELECT * FROM " + table
        df = pd.read_sql_query(sql, con)
        
        #return table as Pandas DataFrame for inspection
        return df 
    
def createKEYSTable(entries, 
                    db = DEFAULTDB, 
                    table = 'KEYS' ):
    ''' Creating the KEYS Table with 
        keyID as AUTOINCREMENTED PRIMARY KEY, 
                #paperID with FOREIGN KEY reference <<--- doesn't exit yet
                                  or does the paer have the keyID as a FK
            
         : param entries : list of list of terms
             : see above
         : param db : str. Name of db. (ie. 'Abstracts.db')
             : default 'Abstracts_DB.db'
         : param table : str. Name of Table to create or insert.
         
         : output : Pandas DataFrame as output for inspection
     '''

    with sqlite3.connect(db) as con:
        print ("Opened %s database successfully" %db); 
        cur = con.cursor() 
        #drops the Abstracts table if it exist in db already
        cur.execute("DROP TABLE IF EXISTS " + table)
        #and recreates it
        cur.execute("CREATE TABLE " + table + "(\
        keyID INTEGER PRIMARY KEY AUTOINCREMENT, \
        keyword TEXT NOT NULL)") 
        
        for keyword in entries:
            cur.execute("INSERT INTO " + table + 
                        "(keyword)\
                        VALUES ('%s')" %keyword);
            #print 'Entry %s added' %keyword
        
        print "Records created successfully";
        
        #return table as Pandas DataFrame for inspection
        sql = "SELECT * FROM " + table
        df = pd.read_sql_query(sql, con)
        return df
