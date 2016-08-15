#DataBases


##Northeastern University Masters of Computer Science


###Independent Project
####Scientific Abstracts Database


- To create a relational database (building upon Python pandas DataFrames and sqlite packages)
- Utilize Flask to launch web application of database for querying abstract database

##Git Folders:
###Some draft folders:
- DataBaseParsing: Parse the scientific abstract text files.  
- - - In directory: Run 'python intialiazeDBstore.py ArchConfAbstracts22/*.txt'
- sqlStart : loads and creates the sqlite database:
- - - In directory: Run 'python load_createSqlDB.py' 

##HERE IS THE MOST IMPORTANT :
###Flask: Includes scripts, templates, etc to run Flask Web App.
- - - Needs to link to database,
- - - In directory: Run 'Flask/app/welcome_flask.py'
- - - Flask/app/ includes the files and scripts to run the Flask app, with templates and static folders here.
- - - Flask/app/scripts are independent python scripts to aid in exspansion of the database and refactoring, improving
- - - Flask/app/scripts also stores the Scientific Abstract Database currently being utilized when running the Flask app by default.

