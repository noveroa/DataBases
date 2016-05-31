''' Attempt to play with terms data
  using set and strips to get into single instances of each terms.
  - Will need to first strip each row entry and then and send to table.
  - regex didn't work, but will try as much faster computationally
  - wondering if one should just create tables and then run a df.apply scheme?
  
'''

'''Need to get terms into lists of the keywords.  
    Assuming each entry should have the keywords/terms only once
'''
terms = set([ e.strip(' \'') for e in terms.strip('[]\'').split(',')])

def createKEYSTable(entries, 
                    db = 'db.db', 
                    table = 'KEYS' ):
   '' Creating the KEYS Table with 
                keyID as AUTOINCREMENTED PRIMARY KEY, 
                #paperID with FOREIGN KEY reference <<--- doesn't exit yet
                                  or does the paer have the keyID as a FK
            
         : param entries : list of list of terms
             : see above
         : param db : str. Name of db. (ie. 'Abstracts.db')
             : default 'Abstracts_DB.db'
         : param table : str. Name of Table to create or insert.
         
         : output : Pandas DataFrame as output for inspection
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
            print 'Entry %s added' %keyword
        
        print "Records created successfully";
        
        #return table as Pandas DataFrame for inspection
        sql = "SELECT * FROM " + table
        df = pd.read_sql_query(sql, con)
        return df
