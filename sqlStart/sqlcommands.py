#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import sqlite3
import pandas as pd

''' Some Starting Point Scripts for creating a SQL DB based on the 
    Abstracts Data parsed into a DataFrame'''

DEFAULTDB = 'Abstracts_DB.db'
DEFAULTHDF = '../DataBaseParsing/DFstore4.h5'


def getPatentDataFrame(hdffile = DEFAULTHDF, 
                       key = 'df'):
    '''Parse a h5 file into readble rows for a Abstracts Table.
       : param hdffile : str. directory location of the h5 file
               default : '../DataBaseParsing/DFstore.h5'
       : param key : str. h5 key for the DF with data.
               default : 'df'
               
       : output : Pandas Dataframe! 
    '''
    
    totalDF = pd.read_hdf(hdffile, key)
    print(totalDF.shape)
        
    return totalDF
    

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



def createTOTALTable(db = DEFAULTDB,
                     table = 'ABSTRACTSTOTAL',
                     data_frame = getPatentDataFrame()):
    '''Add entries to the given db
        
       : param db : str. Name of db. (ie. 'Abstracts.db'
       : param table : str. Name of Table to create or insert.
       : param data_frame : Pandas DataFrame. Insert into given table by row.
       
       
       : output : Pandas DataFrame for inspection, 
       : output : sql table created with rows inserted.
      
    '''
  
    with sqlite3.connect(db) as con:
        cur = con.cursor() 
        #drops the Abstracts table if it exist in db already
        cur.execute("DROP TABLE IF EXISTS " + table)
        #and recreates it
        cur.execute("CREATE TABLE " + table +
                    "(\
                    Abstract TEXT, \
                    'Author affiliation' TEXT, \
                    Authors TEXT, \
                    Conf TEXT, \
                    Title TEXT, \
                    terms TEXT,\
                    year INT\
                    )");

        data_frame.to_sql(table, con, flavor='sqlite', 
                       schema=None, if_exists='append', 
                       index=False, index_label=None,
                       chunksize=None, dtype=None)
        
        sql = "SELECT * FROM " + table
        df = pd.read_sql_query(sql, con)
        
        #return table as Pandas DataFrame for inspection
        return df  

def createConfTable(data_frame,
                    db = 'test.db', 
                    DFCol = 'Conf',
                    table = 'CONFERENCES',
                    tableCol = ['confName']
                  ):
    
    ''' Creating the CONFERENCES Table with AutoIncremented PRIMARY Key as ConfID
         : param data_frame : Pandas DataFrame from which to create the CONFERENCE TABLE
         : param db : str. Name of db. (ie. 'Abstracts.db')
             : default 'test.db'
         : param DFCol : string Column name of data_frame with information.
             : default = 'Conf'
             : alternatively : enter with already unique table.
         : param table : str. Name of Table to create or insert.
             : default : CONFERENCES
         : param tableCol : tuple of str. Table keyword as a tuple of string
         
         : output : Pandas DataFrame as output for inspection
         : output : sql table created with rows inserted.
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
    
        dfConf = pd.DataFrame(data_frame[DFCol].unique(), columns = tableCol)
        print ('Created DataFrame')
    
        dfConf.to_sql(table, con, flavor='sqlite', 
                    schema=None, if_exists='append', 
                    index=False, index_label=None,
                    chunksize=None, dtype=None)
        print("Records created successfully");
        
    sql = "SELECT * FROM " + table
    df = pd.read_sql_query(sql, con)
        
        #return table as Pandas DataFrame for inspection
    return df  
        
def createPublicationsTable(data_frame, 
                            db = DEFAULTDB,
                            DFCol = ('Conf', 'year'),
                            table = 'PUBLICATIONS',
                            tableCol = ['confName', 'year'],
                            foreignKey = 'CONFERENCES'):
    ''' Creating the PUBLICATIONS Table with AutoIncremented PRIMARY Key as pubID
             : param data_frame : Pandas DataFrame from which to create the PUBLICATIONS TABLE
             : param db : str. Name of db. (ie. 'Abstracts.db')
                 : default 'test.db'
             : param DFCol : tuple of strings Column names of data_frame with groupby cols.
                 : default = 'Conf'
                 : alternatively : enter with already unique table.
             : param table : str. Name of Table to create or insert.
                 : default : PUBLICATIONS
             : param tableCols : tuple of str. Table keywords as tuple of strings
                 : default  : ('confName', 'year')
             : param foreignKey : str . Name of Foreign key table as str
         
             : output : Pandas DataFrame as output for inspection
             : output : sql table created with rows inserted.
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
        data = list(data_frame.groupby(DFCol).count().index.get_values())
        dfPubs = pd.DataFrame(data, columns = tableCol)
        print('Created DataFrame')
        #insert into the table
        dfPubs.to_sql(table, con, flavor='sqlite', 
                    schema=None, if_exists='append', 
                    index=False, index_label=None,
                    chunksize=None, dtype=None)
        print("Records created successfully");
        
    sql = "SELECT * FROM " + table
    dfPubs = pd.read_sql_query(sql, con)
        
        #return table as Pandas DataFrame for inspection
    return dfPubs           

    
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
    
def createKEYSTable(data_frame, 
                    db = DEFAULTDB, 
                    DFCol = 'terms',
                    table = 'KEYS' ,
                    tableCol = ['keyword']
                   ):
    ''' Creating the KEYS Table with 
        keyID as AUTOINCREMENTED PRIMARY KEY, 
             : param data_frame : Pandas DataFrame from which to create the KEYS TABLE
             : param db : str. Name of db. (ie. 'Abstracts.db')
                 : default 'test.db'
             : param DFCol : tuple of strings Column names of data_frame with groupby cols.
                 : default = 'terms'
                 : alternatively : enter with already unique table.
             : param table : str. Name of Table to create or insert.
                 : default : KEYS
             : param tableCols : tuple of str. Table keywords as tuple of strings
                 : default  : ('keyword')
             
             :***NEED TO CREATE COMPOSITE***
         
             : output : Pandas DataFrame as output for inspection
             : output : sql table created with rows inserted.
         '''
    
    def findTermSet(data_frame, DFCol = DFCol):
        ''' Parse the TOTALABSTRACTS table dataframe terms column.
        Create a single set of all terms
        
        : param tableDF : a Pandas DataFrame (ie TOTALABSTRACTS table as DF)
        : param keyword : column name to be recast and set of terms found from
        
        : output : a master set of terms set as a list (no duplicates)
        '''
    
        
    
        #recast - since made a string during the entry into the sqlite db.
        terms = data_frame[DFCol].apply(lambda x: set([ e.strip(' \'') for e in x.strip('[]\'').split(',')]))
    
        #create a single set
        termset = list(frozenset().union(*terms))
        return pd.DataFrame(termset, columns = tableCol)
    
    with sqlite3.connect(db) as con:
        print ("Opened %s database successfully" %db); 
        cur = con.cursor() 
        #drops the Abstracts table if it exist in db already
        cur.execute("DROP TABLE IF EXISTS " + table)
        #and recreates it
        cur.execute("CREATE TABLE " + table + "(\
        keyID INTEGER PRIMARY KEY AUTOINCREMENT, \
        keyword TEXT NOT NULL)") 
        
        keyDF1 = findTermSet(data_frame)
        
        print keyDF1.head()
        print('Created DataFrame')
        #insert into the table
        keyDF1.to_sql(table, con, flavor='sqlite', 
                    schema=None, if_exists='append', 
                    index=False, index_label=None,
                    chunksize=None, dtype=None)
        print("Records created successfully");
        
    sql = "SELECT * FROM " + table
    dfKeys = pd.read_sql_query(sql, con)
        
        #return table as Pandas DataFrame for inspection
    return dfKeys  

def createAUTHORSTable(data_frame, 
                    db = DEFAULTDB, 
                    DFCol = 'Authors',
                    table = 'AUTHORS' ,
                    tableCol = ['AuthorName']
                   ):
    ''' Creating the AUTHORS Table with 
            authorID as AUTOINCREMENTED PRIMARY KEY, 
             : param data_frame : Pandas DataFrame from which to create the AUTHORS TABLE
             : param db : str. Name of db. (ie. 'Abstracts.db')
                 : default 'test.db'
             : param DFCol : tuple of strings Column names of data_frame with groupby cols.
                 : default = 'Authors'
                 : alternatively : enter with already unique table.
             : param table : str. Name of Table to create or insert.
                 : default : AUTHORS
             : param tableCols : tuple of str. Table keywords as tuple of strings
                 : default  : ('AuthoName')
             : **NEED TO CREATE COMPOSITE **
         
             : output : Pandas DataFrame as output for inspection
             : output : sql table created with rows inserted.
         '''
    
    def findAuthorsSet(data_frame, DFCol = DFCol):
        ''' Parse the TOTALABSTRACTS table dataframe terms column.
        Create a single set of all terms
        
        : param data_frame : a Pandas DataFrame (ie TOTALABSTRACTS table as DF)
        : param DFCol : column name to be recast and set of terms found from
        
        : output : a master set of terms set as a list (no duplicates)
        '''
        import re
        commaQuote = re.compile('[\',]')
        
    
        #recast - since made a string during the entry into the sqlite db.
        authors = data_frame[DFCol].apply(lambda a: a.strip("[]'"))
        authors = authors.apply(lambda x: filter(lambda a: a != '',
                                                  commaQuote.sub(' ', x).split('   ')))
        
        
        #create single set and remove leading white space
        authors = list(frozenset().union(*authors))
        authors = [anew.strip(' ') for anew in authors]
        #need to reset becuase of the white space
        return list(set(authors))
    with sqlite3.connect(db) as con:
        print ("Opened %s database successfully" %db); 
        cur = con.cursor() 
        #drops the Authors table if it exist in db already
        cur.execute("DROP TABLE IF EXISTS " + table)
        #and recreates it
        cur.execute("CREATE TABLE " + table + "(\
        authorID INTEGER PRIMARY KEY AUTOINCREMENT, \
        AuthorName TEXT \
        )") 
        authors = findAuthorsSet(data_frame)
        print ('Author set created')
        
        #only take 1 -> becuase first is empty
        authorsDF = pd.DataFrame(authors[1:], columns = tableCol)
        
        #insert into the table
        authorsDF.to_sql(table, con, flavor='sqlite', 
                    schema=None, if_exists='append', 
                    index=False, index_label=None,
                    chunksize=None, dtype=None)
        print("Records created successfully");
        
    sql = "SELECT * FROM " + table
    dfAuthors = pd.read_sql_query(sql, con)
        
    #return table as Pandas DataFrame for inspection
    return authors, dfAuthors

def createAFFILIATIONTable(data_frame, 
                    db = 'test3.db', 
                    DFCol = 'Author affiliation',
                    table = 'AFFILIATIONS' ,
                    tableCol = ['affiliation']
                   ):
    ''' Creating the AFFILIATIONS Table with 
        keyID as AUTOINCREMENTED PRIMARY KEY, 
             : param data_frame : Pandas DataFrame from which to create the AFFILIATIONS TABLE
             : param db : str. Name of db. (ie. 'Abstracts.db')
                 : default 'test.db'
             : param DFCol : tuple of strings Column names of data_frame with groupby cols.
                 : default = 'Author affiliation'
                 : alternatively : enter with already unique table.
             : param table : str. Name of Table to create or insert.
                 : default : AFFILATIONS
             : param tableCols : tuple of str. Table keywords as tuple of strings
                 : default  : ('affiliation')
             
             : output : Pandas DataFrame as output for inspection
             : output : sql table created with rows inserted.
         '''
    
    def findAffiliationSet(data_frame, DFCol = DFCol):
        ''' Parse the TOTALABSTRACTS table dataframe terms column.
        Create a single set of all terms
        
        : param tableDF : a Pandas DataFrame (ie TOTALABSTRACTS table as DF)
        : param keyword : column name to be recast and set of terms found from
        
        : output : a master set of terms set as a list (no duplicates)
        '''
        #recast - since made a string during the entry into the sqlite db.
        affiliation = data_frame[DFCol]
    
        #create unique using .unique()
        
        return pd.DataFrame(affiliation.unique(), columns = tableCol)
    
    with sqlite3.connect(db) as con:
        print ("Opened %s database successfully" %db); 
        cur = con.cursor() 
        #drops the Abstracts table if it exist in db already
        cur.execute("DROP TABLE IF EXISTS " + table)
        #and recreates it
        cur.execute("CREATE TABLE " + table + "(\
        affilID INTEGER PRIMARY KEY AUTOINCREMENT, \
        affiliation TEXT NOT NULL)") 
        
        affilDF = findAffiliationSet(data_frame)
        print('Created DataFrame')
        #insert into the table
        affilDF.to_sql(table, con, flavor='sqlite', 
                    schema=None, if_exists='append', 
                    index=False, index_label=None,
                    chunksize=None, dtype=None)
        print("Records created successfully");
        
    sql = "SELECT * FROM " + table
    dfAffil = pd.read_sql_query(sql, con)
        
        #return table as Pandas DataFrame for inspection
    return dfAffil