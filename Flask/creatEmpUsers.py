import sqlite3
import pandas as pd

with sqlite3.connect('EmpData') as con:
    
    print ("Opened database successfully"); 
    cur = con.cursor() 
        #drops the Abstracts table if it exist in db already
    cur.execute("DROP TABLE IF EXISTS USERS")
        #and recreates it
    cur.execute("CREATE TABLE User(\
        userID INTEGER PRIMARY KEY AUTOINCREMENT, \
        userName TEXT NOT NULL,\
        password TEXT NOT NULL)") 
        
    cur.execute("INSERT INTO User VALUES(3,'Admin', 'admin')")
    con.commit() 
    print("Table created successfully");