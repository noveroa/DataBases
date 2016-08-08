#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import sqlite3
import pandas as pd

DEFAULTDB = 'Abstracts_aug4.db'
DEFAULTJSON = "json4.json"

def jsonDF(jsonFile):
    '''Create a pandas dataframe from a Json File
    '''
    f = open(jsonFile, "r+")
    return pd.read_json(f, orient='index')

def sqlCMDToPD(table, 
               db = DEFAULTDB):
    '''Take a sql db and return as a readable pandas DataFrame
       : param db : str. Name of db. (ie. 'Abstracts.db'
       : param sqlcmd : str. Sqlite3 cmd to execute. 
               default: "SELECT * FROM Abstracts" 
                           > select all from Abstracts table
    '''
    
    #connect to a db
    with sql.connect(db) as con:
        
        #run command
        sqlcmd = "SELECT * FROM '%s'" %table
        df = pd.read_sql_query(sqlcmd, con)
        
        # Check resulting pandas DF shape
        print df.shape
        
        return df

def getContents():
    '''
    : param NONE
    : output : Returns a json dictionary of the table names, entry counts, and links to tables 
                of all table names in the database
    ''' 
    with sql.connect(mydb) as con:
    
        cursor = con.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        mytables = (cursor.fetchall())
        myt = [t[0] for t in mytables]
        
        return myt
    
def insert_toTable(db, df, table = 'ABSTRACTSTOTAL'):
    '''Check to insert a new record into a database table, inserts if does not exist
    param  db str : Database name to connect to
    param df pandas dataframe : dataframe being inspected for entry
    param table str : Table Name to insert into, if does not exist will create
    output : new entry inserted
    '''
    with sql.connect(db) as con:
        df.to_sql(table, con, flavor='sqlite', 
                      schema=None, if_exists='append',
                      index=False, index_label=None,
                      chunksize=None, dtype=None)
            
        print("Records %s inserted"%table)
    
def insertcheckRecord(db, df, table = 'CONFERENCES', un = 'confName' ):
    '''Check to insert a new record into a database table, inserts if does not exist
    param  db str : Database name to connect to
    param df pandas dataframe : dataframe being inspected for entry
    param table str : Table Name to insert into, if does not exist will create
    param un str : unique column to check for entry to create a new pk, if not will just append
    '''
    t = sqlCMDToPD(table, mydb)
    if df[un][0] not in t[un].unique():
        insert_toTable(db, df[un], table)
        return True
    else:
        print(" %s already exists, try upserting with key value or deleting" %df[un][0])
        return False  
    
def insertcheckRecordTWO(db, df, table = 'PUBLICATIONS', un = 'confName', un1 = 'year' ):
    '''Check to insert a new record into a database table, inserts if does not exist, checks for multiple
    entries as unique
    param  db str : Database name to connect to
    param df pandas dataframe : dataframe being inspected for entry
    param table str : Table Name to insert into, if does not exist will create
    param un str : unique column to check for entry to create a new pk, if not will just append
    param un1 str : unique column2 to check for entry to create a new pk, if fail un, if not will just append
    '''
    t = sqlCMDToPD(table, mydb)
    if df[un][0] not in t[un].unique():
        print df[un][0], 'is new'
        insert_toTable(db, df[[un, un1]], table)
    else:
        
        tmp = t.query('@conf == confName') 
        
        if df[un1][0] not in tmp[un1].unique():
            print (df[[un, un1]].values), 'is a new entry'
            insert_toTable(db, df[[un, un1]], table)
        else:
            print(" %s already exists, try upserting with key value or deleting" %df[[un, un1]].values)


def insertValue(db, table, value):
    '''Insert a new record by value into a database table
    param  db str : Database name to connect to
    param table str : Table Name to insert into, if does not exist will create
    param value str : unique value entered into table
    '''
    with sql.connect(db) as con:
        con.execute("INSERT INTO {tn} VALUES(NULL,'%s')".format(tn=table)%value)
        print('%s inserted into %s')%(value, table)
        
def enterValueCheck_nested(db, table, values, cn):
    '''Check to insert a new record into a database table, inserts if does not exist
    param  db str : Database name to connect to
    param table str : Table Name to insert into, if does not exist will create
    param values python series : series being parsed and formated to inspection and entry into table
    param cn str : column name to check for entry to create a new pk
    '''
    tableDF = sqlCMDToPD(table, db)
    for i, ky in enumerate(values):
        for key in ky.split(','):
            if key not in tableDF[cn].unique():
                print key, 'is new'
                insertValue(db, table, key)
            else:
                print key, 'already exists in table'
                
def deleteRowPK(db, table, pkcol, entryID):
    '''Deleting a Record by PRIMARY KEY
    param  db str : Database name to connect to
    param table str : Table Name to delete from
    param pkcol str : primary column name being used, 
    param entryID int : integer value (Primary Key Value) to delete from table
    '''
    with sql.connect(db) as con:
        
        con.execute("DELETE FROM {tn} WHERE {idf}={my_id}".format(tn=table, idf=pkcol, my_id=entryID))

        con.commit()

def deleteRowOTHER(db, table, cn, entry):
    '''Deleting a Record
    param  db str : Database name to connect to
    param table str : Table Name to delete from
    param cn str : column name being used for deletion comparason (if no PK column, ie, abstracts Total)
    param entry str : the str to be used to find and remove records (removes all records
    '''
    with sql.connect(db) as con:
        
        con.execute("DELETE FROM {tn} WHERE {idf}='%s'".format(tn=table, idf=cn)%entry)

        con.commit()


        
def entryintotables(db, jsonfile):
    '''Inserting a Record from a JsonFile
    param  db str : Database name to connect to
    param jsonfile str : name of Json File to be read into the database
    '''
    f = open(jsonfile, "r+")
    jdf = pd.read_json(f, orient='index')
    jdf.Conf = 'WAKA'
    #TOTALABSTRACTS, check and then insert if needed, uniqueness based on Abstract column
    #insertcheckRecord(db, jdf, table = 'ABSTRACTSTOTAL', un =  'Abstract')
    
    #renaming of columns
    jdf.rename(columns = {'Conf':'confName'}, inplace= True)
    
    #CONFERENCES, check and then insert if needed, uniqueness based on Abstract column
    insertcheckRecord(db, jdf, table = 'CONFERENCES', un = 'confName' )
    
    #PUBLICATIONS, check and then insert if needed, uniqueness based on Abstract column
    insertcheckRecordTWO(db, jdf, table = 'PUBLICATIONS', un = 'confName', un1 = 'year' )
    
    #AFFILIATIONS
    jdf.rename(columns = {'Author affiliation' : 'affiliation'}, inplace = True)
    insertcheckRecord(db = db, df = jdf, table = 'AFFILIATIONS', un = 'affiliation')
    
    #For the nested: authors, keywords, and need to reparse/reformat, also to show numerous ways to insert:
    #KEYS
    enterValueCheck_nested(db=db, table = 'KEYS', values = jdf.terms, cn = 'keyword')
    #AUTHORS
    enterValueCheck_nested(db=db, table = 'AUTHORS', values = jdf.Authors, cn = 'authorName')
    
    #enter
    return jdf