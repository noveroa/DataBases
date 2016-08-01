#DataBases


##Northeastern University Masters of Computer Science


###Independent Project
####Scientific Abstracts Database


- To create a relational database (building upon Python pandas DataFrames and sqlite packages)
- Utilize Flask to launch web application of database for querying abstract database

- Git Folders:
- - DataBaseParsing: Parse the scientific abstract text files.  
- - - In directory: Run 'python intialiazeDBstore.py ArchConfAbstracts22/*.txt'

- - sqlStart : loads and creates the sqlite database:
- - - In directory: Run 'python load_createSqlDB.py' 

- - Flask: Includes scripts, templates, etc to run Flask Web App.
- - - Needs to link to database, currently to sqlStart/Abstracts_aug1.db
- - - In directory: Run 'Flask/app/welcome_flask.py'

