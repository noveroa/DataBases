#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import sqlite3
import pandas as pd

''' Some Starting Point Scripts for creating a SQL DB based on the 
    Abstracts Data parsed into a DataFrame'''


def sqlCMDToPD(db, sqlcmd = "SELECT * FROM Abstracts"):
    '''Take a sql db and return as a readable pandas DataFrame
       : param db : str. Name of db. (ie. 'Abstracts.db'
       : param sqlcmd : str. Sqlite3 cmd to execute. 
               default: "SELECT * FROM Abstracts" 
                           > select all from Abstracts table
    '''
    
    #connect to a db
    with sqlite3.connect(db) as con:
        
        #run command
        df = pd.read_sql_query(sqlcmd, con)
        
        # Check resulting pandas DF shape
        print df.shape
        
        return df

def parseDataFrame(hdffile = '../DataBaseParsing/DFstore.h5', key = 'df'):
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
        rows.extend([x[0:9]])
        
    return rows
    

def addAbstractsTable(db, entries):
    '''Add entries to the given db
       : param db : str. Name of db. (ie. 'Abstracts.db'
       : param entries : list of tuples 
           : [(1, 'Audi', 'A', 'B', 'C', 'D', 'E', 'F', 'G'),
              (2, 'Passat', 'H', 'I', 'C', 'D', 'J', 'K', 'Z')
              ]
    '''
    with sqlite3.connect(db) as con:
        cur = con.cursor() 
        #drops the Abstracts table if it exist in db already
        cur.execute("DROP TABLE IF EXISTS Abstracts")
        #and recreates it
        cur.execute("CREATE TABLE Abstracts(ID INT, Abstract TEXT, 'Author affiliation' TEXT, \
        Authors TEXT, 'Classification Code' TEXT, Conf TEXT, Database TEXT, Source TEXT, \
        Title TEXT)")

        cur.executemany("INSERT INTO Abstracts VALUES(?,?,?,?,?,?,?,?, ?)", entries )

    
 