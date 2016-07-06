
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from cStringIO import StringIO
import base64
import seaborn as sns


def getPieOne(df, conference):
    fig = plt.figure()
    fig = df.plot(kind = 'pie', 
                  colormap = 'Blues', 
                  title = conference, 
                  subplots = True, 
                  legend = False, 
                  labels = ['' for x in np.arange(len(df))])
    plt.ylabel('')
    plt.legend( list(df.index), 
               bbox_to_anchor=(1.1, 1),
              fontsize = "xx-small")
    
    io = StringIO()
    plt.savefig(io, format='png')
    img = base64.encodestring(io.getvalue())
   
    io = StringIO()
    plt.savefig(io, format='png')
    data = base64.encodestring(io.getvalue())
    script = '''<img src="data:image/png;base64,{}";/>'''
    plt.close()
    return script.format(data)


def getBar(df, conference, xaxis, yaxis, orientation, ylabel = 'count', xlabel = 'trada'):
    plt.cla()
    fig = sns.barplot(data = df, 
                      y =  yaxis,#'keyword', 
                      x = xaxis, #'count', 
                      palette='Blues', 
                      orient = orientation)
    fig.set_ylabel(ylabel)
    fig.set_xlabel(xlabel)
    
    #for l in fig.get_ymajorticklabels():
        #l.set_visible(False)
    io = StringIO()
    plt.savefig(io, format='png')
    img = base64.encodestring(io.getvalue())
   
    io = StringIO()
    plt.savefig(io, format='png')
    data = base64.encodestring(io.getvalue())
    script = '''<img src="data:image/png;base64,{}";/>'''
    plt.close()
    return script.format(data)


def getHeatMap(data_frame, indexCol = 'confName', cols = 'pubYear', vals = 'counts', annotation = False):
    plt.cla()
    
    fig = sns.heatmap(data_frame.pivot_table(index=indexCol, 
                                             columns=cols, 
                                             values=vals),
                                             annot = annotation,
                                             cmap = 'Blues')
    
    
    io = StringIO()
    plt.savefig(io, format='png')
    img = base64.encodestring(io.getvalue())
   
    io = StringIO()
    plt.savefig(io, format='png')
    data = base64.encodestring(io.getvalue())
    script = '''<img src="data:image/png;base64,{}";/>'''
    plt.close()
    return script.format(data)

def getLine(data_frame, xaxis = 'confName', yaxis = 'counts'):
    plt.cla()
    fig = sns.swarmplot(data = data_frame, 
                        x=xaxis, 
                        y = yaxis,
                        palette = 'Blues')
    
    io = StringIO()
    plt.savefig(io, format='png')
    img = base64.encodestring(io.getvalue())
   
    io = StringIO()
    plt.savefig(io, format='png')
    data = base64.encodestring(io.getvalue())
    script = '''<img src="data:image/png;base64,{}";/>'''
    return script.format(data)



##DRAFTS##
def getPie2():
    import matplotlib.pyplot as plt

    with sqlite3.connect(mydb) as con:
        sqlcmd = "SELECT Conf, Year FROM ABSTRACTSTOTAL"
        df = pd.read_sql_query(sqlcmd, con)
        keys = list(df['Conf'].unique())
    
        fig, axes = plt.subplots(nrows=len(keys) + 1, ncols=1,
                             sharex=False
                            )
        fig = df.groupby(['Conf'])["Conf"].count().plot(kind = 'pie', colormap = 'ocean', 
                                                subplots = True, ax = axes[0] )    
        for i, conference in enumerate(keys):
            fig = df.query('Conf == "%s"' % conference).groupby('year').count().plot(kind = 'pie', 
                                                                           ax = axes[i+1],
                                                                           colormap = 'ocean',
                                                                           subplots = True)
                                                    
                                                                          
        html = '''
        <html>
        <head>
         <h1> Conferences by year %s</h1>
        </head>
        <body> 
        
            <img src="data:image/png;base64,{}" />
        
        </body>
        </html>
        '''
        io = StringIO()
        plt.savefig(io, format='png')
        data = base64.encodestring(io.getvalue())

    return html.format(data)


def getPie(start):
    df = pd.DataFrame(start[["Conf", "year"]])
    fig = plt.figure()
    
    df.groupby(['Conf'])["Conf"].count().plot(kind = 'pie', 
                                              colormap = 'ocean', 
                                              subplots = True, 
                                              title = 'Conferences', 
                                              )
    for conference in df['Conf'].unique():
        df.query('Conf == "%s"' % conference).groupby('year').count().plot(kind = 'pie', 
                                                                           subplots = True,
                                                                           colormap = 'ocean',
                                                                           title = conference, 
                                                                          )
        plt.legend(bbox_to_anchor=(1, 1), bbox_transform=plt.gcf().transFigure)
    
    io = StringIO()
    plt.savefig(io, format='png')
    data = base64.encodestring(io.getvalue())

    return html.format(data)
    
def getBardd(df, conference):
    plt.figure()
    fig =  df.plot(kind = 'bar', 
                   colormap = 'ocean', 
                   title = conference, 
                   subplots = True,
                   legend = False)
   
    io = StringIO()
    plt.savefig(io, format='png')
    img = base64.encodestring(io.getvalue())
   
    io = StringIO()
    plt.savefig(io, format='png')
    data = base64.encodestring(io.getvalue())
    script = '''<img src="data:image/png;base64,{}";/>'''
    plt.close()
    return script.format(data)
