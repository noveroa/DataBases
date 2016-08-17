import sys
import sqlite3 as sql
import pandas as pd
import f_RESTful as r

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

def deleteRowTABLE(db, paperID, table = 'ABSTRACTSTOTAL'):
    '''Deleting a Record by PRIMARY KEY
    param  db str : Database name to connect to
    param paperID int : integer value (Primary Key Value) to delete from table
    param table str : Table Name to delete from
    '''
    values = selectPaperID(db, paperID)
    print values
    with sql.connect(db) as con:
       
        con.execute("DELETE FROM {tn} WHERE Abstract = '%s' AND Conf= '%s' AND year = '%s'".format(tn=table)%(values[0], values[1], values[2]))

        df = r.sqlCMDToPD('ABSTRACTSTOTAL', db)
    
        return df
def mergeDelKEYS(db, paperID, table1, pk1, table2, pk2, table3, pk3, evaluate):
    sqlcmd1 = '''
    SELECT {tn1}.%s, {tn2}.%s
    FROM {tn1}
    JOIN {tn2}
    ON {tn1}.%s = {tn2}.%s
    '''.format(tn1 = table1, tn2= table2)%(pk1, pk2, pk1, pk1)

    #sqlcmd2a =  ''' SELECT * FROM {tn3} WHERE %s IN %s '''.format(tn3 = table3)%(pk2, values)
    
    sqlcmd2 = '''
    SELECT {tn2}.%s
    FROM {tn1}
    JOIN {tn2}
    ON {tn1}.%s = {tn2}.%s
    WHERE {tn1}.%s = {myid}
    '''.format(tn1 = table1, tn2= table2, myid = paperID)%(pk2, pk1, pk1, pk1)

    
    
    with sql.connect(db) as con:
        #get all papers and their keywords
        df= pd.read_sql(sqlcmd1, con)
        #get all keywords in my paper
        df2 = pd.read_sql(sqlcmd2, con)
        vals = tuple(eval(d).encode('utf-8') for d in df2[pk2])
        #get the keyword IDs given the keywords
        sqlcmd3 =  ''' SELECT * FROM {tn3} WHERE %s IN %s '''.format(tn3 = table3)%(pk2, vals)
        
        df3 = pd.read_sql(sqlcmd3, con)
        
        if evaluate:
            df[pk2] = df[pk2].apply(lambda k : eval(k))
        
        #merge the all papers and keywords with only keywords in paper. If count < = 1, remove from KEYS table
        c = pd.merge(df, df3)
        c = pd.DataFrame(c.groupby([pk2,
                                    pk3]).size()
                        ).reset_index().rename(columns = {0:'Count'}).query('Count <= 1')
        
        return c


def deletefromKEYS(paperID, pkcol, db, mpkcol = 'keyID'):
    keys = mergeDelKEYS(db, paperID, 'PAPER','paperID', 'PAPERKEY', 'keyword', 'KEYS', 'keyID', evaluate = True)
    #need to delete keys from PAPERKEY based on PaperID now
    r.deleteRowPK(db, 'PAPERKEY', pkcol, paperID)
    
    deleted = [x for x in keys[mpkcol].apply(lambda key: r.deleteRowPK(db = db, 
                                                                    table = 'KEYS', 
                                                                    pkcol = mpkcol, 
                                                                    entryID =key))]
    return deleted

def mergeDelAffil(db, paperID, table1, pk1, table2, pk2, table3, pk3):
    sqlcmd1 = '''
    SELECT {tn1}.%s, {tn2}.%s
    FROM {tn1}
    JOIN {tn2}
    ON {tn1}.%s = {tn2}.%s
    '''.format(tn1 = table1, tn2= table2)%(pk1, pk2, pk1, pk1)

    #sqlcmd2a =  ''' SELECT * FROM {tn3} WHERE %s IN %s '''.format(tn3 = table3)%(pk2, values)
    
    sqlcmd2 = '''
    SELECT {tn2}.%s
    FROM {tn1}
    JOIN {tn2}
    ON {tn1}.%s = {tn2}.%s
    WHERE {tn1}.%s = {myid}
    '''.format(tn1 = table1, tn2= table2, myid = paperID)%(pk2, pk1, pk1, pk1)

    
    
    with sql.connect(db) as con:
        #get all papers and their keywords
        df= pd.read_sql(sqlcmd1, con)
        #get all keywords in my paper
        df2 = pd.read_sql(sqlcmd2, con)
        vals = df2[pk2].values[0]
            
        #get the keyword IDs given the keywords
        sqlcmd3 =  ''' SELECT * FROM {tn3} WHERE {pkcol} = {my_id} '''.format(tn3 = table3, pkcol = pk2, my_id = vals)
        
        df3 = pd.read_sql(sqlcmd3, con)
        
        #merge the all papers and keywords with only keywords in paper. If count < = 1, remove from KEYS table
        c = pd.merge(df, df3)
        c = pd.DataFrame(c.groupby([pk2,
                                   pk3]).size()
                        ).reset_index().rename(columns = {0:'Count'}).query('Count <= 1')
        
        return c


def deletefromAFFILIATIONS(paperID, pkcol, db, mpkcol = 'affilID'):
    keys = mergeDelAffil(db, paperID, 'PAPER', 'paperID', 'AFFILIATIONPAPER', 'affilID', 'AFFILIATIONS', 'affiliation')
    #need to delete keys from PAPERKEY based on PaperID now
    r.deleteRowPK(db, 'AFFILIATIONPAPER', pkcol, paperID)
    
    deleted = [x for x in keys[mpkcol].apply(lambda key: r.deleteRowPK(db = db, 
                                                                    table = 'AFFILIATIONS', 
                                                                    pkcol = mpkcol, 
                                                                    entryID = key
                                                                     )
                                             )]
    return deleted

def deletebyPaper(pk, pkcol = 'paperID', db = DEFAULTDB):
    '''Deleting a Record from datbase by paperID
    param pk int : integer value (Primary Key Value) to delete from table
    param pkcol str : primary column name being used,
    param  db str : Database name to connect to
    '''

    print (pk)
    #delete from KEYS
    deletefromKEYS(pk, pkcol, db)
    
    #delete from Affiliations
    deletefromAFFILIATIONS(pk, pkcol, db)
    
    
    #delete from composites (within deleting from Keys)
    #r.deleteRowPK(db, 'PAPERKEY', pkcol, pk)
    #r.deleteRowPK(db, 'AFFILIATIONPAPER', pkcol, pk)
    r.deleteRowPK(db, 'PAPERAUTHOR', pkcol, pk)

    

    #delete from TOTAL ABSTRACTS
    deleteRowTABLE(db, pk)

    #delete the paper from paperTable LAST!
    r.deleteRowPK(db, 'PAPER', pkcol, pk)
    
    print 'Deletion Complete'
   