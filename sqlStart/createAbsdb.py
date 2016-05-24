#!/usr/bin/python
# -*- coding: utf-8 -*-

import sqlite3 as lite
import sys

''' creating a new table in the createAbsdb.db : Abstracts 
    : params NONE
    : output SQLite Table: Abstracts
            :rows : Id INT, Name TEXT, Price INT
            :rows : Abstract TEXT, Author affiliation TEXT, Authors TEXT, Classification Code TEXT,
                    Conf TEXT, Database TEXT, Source TEXT, Title TEXT, terms TEXT, year TEXT
            tutorial: http://zetcode.com/db/sqlitepythontutorial/
'''

#list of the records to add
##add hdf read text and pandas frame here?


con = lite.connect('Abstracts.db')

with con:
    
    cur = con.cursor()    
    
    #drops the cars table if it exist already 
    cur.execute("DROP TABLE IF EXISTS Abstracts")
    #and recreates it
    cur.execute("CREATE TABLE Abstracts(Abstract TEXT, 'Author affiliation' TEXT,\
    Authors TEXT, 'Classification Code' TEXT, Conf TEXT, Database TEXT, Source TEXT, \
    Title TEXT, terms TEXT, year TEXT)")
    
    #The first parameter of this method is a parameterized SQL statement. 
    #The second parameter is the data, in the form of tuple of tuples.
    #cur.executemany("INSERT INTO Abstracts VALUES(?, ?, ?, ?, ?, ?, ?,? ?)", Abstracts)