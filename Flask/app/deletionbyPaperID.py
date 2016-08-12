import sys
import sqlite3 as sql
import pandas as pd
import RESTful as r

''' Delete by PaperID : removes instances of the given paperID from the composite tables, paper table and
the TOTALABSTRACTS table.  Not removed from the others as they are not unqiue to given paper'''

DEFAULTDB = 'scripts/Abstracts_aug12.db'

def selectPaperID(db, paperID):
    '''
    : param NONE
    : output : Returns a json dictionary of the table names, entry counts, and links to tables 
                of all table names in the database
    ''' 
    with sql.connect(db) as con:
        c = con.cursor()
        c.execute("SELECT abstract, confName, pubYear FROM PAPER WHERE paperID = {my_id} ".format(my_id = paperID)) 
        x = c.fetchone()
        return x

def deleteRowTABLE(db, paperID):
    '''Deleting a Record by PRIMARY KEY
    param  db str : Database name to connect to
    param table str : Table Name to delete from
    param pkcol str : primary column name being used, 
    param entryID int : integer value (Primary Key Value) to delete from table
    '''
    values = selectPaperID(db, paperID)
    print values
    with sql.connect(db) as con:
       
        con.execute("DELETE FROM {tn} WHERE Abstract = '%s' AND Conf= '%s' AND year = '%s'".format(tn='ABSTRACTSTOTAL')%(values[0], values[1], values[2]))

        df = r.sqlCMDToPD('ABSTRACTSTOTAL', db)
    
        return df

def deletebyPaper( myID, db = DEFAULTDB):
    

    print (myID)
    #delete from composites
    r.deleteRowPK(db, 'PAPERKEY', 'paperID', myID)

    r.deleteRowPK(db, 'PAPERAUTHOR', 'paperID', myID)

    r.deleteRowPK(db, 'AFFILIATIONPAPER', 'paperID', myID)

    #delete from TOTAL ABSTRACTS
    
    deleteRowTABLE(db, myID)

    #delete the paper from paperTable LAST!
    r.deleteRowPK(db, 'PAPER', 'paperID', myID)
    
    print 'Deletion Complete'
    