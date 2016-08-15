#!/usr/bin/env python
"""

Code care of https://github.com/amueller wordcloud conda package.
to install : pip install wordcloud or conda install -c https://conda.anaconda.org/amueller wordcloud

REQUIREMENTS: PIL

"""
import sys, os
import welcome_flask3 as flaskapp

#import libraries for generating the wordcloud
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
from cStringIO import StringIO
import base64
from wordcloud import WordCloud# STOPWORDS#, ImageColorGenerator
import random


def prep_KWcloud(grouper, 
                 group, 
                 grouped):
    '''
    : param grouper str: column by which to group table by (i.e 'confName', 'pubYear')
    :       default 'paperID'
    : param group str/int: group to return results of (ie. 'ECSA', 'WICSA', 2009, 2014)
    :       default ''
    : grouped boolean : Boolean True if to render specified group (ie, conference or year)
    :       default False
    : output : string of keywords separated by spaces (each multi word keyword space repplaced by '_')
    '''
    
    mergedDF, groupedDF = flaskapp.getPapersKWgroup(grouper)
    
    if grouped:
        calculatedGroup = groupedDF.get_group(group)
    else:
        calculatedGroup = mergedDF
    
    entries = ""
    for each in calculatedGroup['keyword']:
        
        entry = "".join([key.replace(" ", "_") for key in each])
        
        entries = " ".join((entries, entry))
    
    return entries

def prep_Aucloud():
    
    data_frame = flaskapp.getAuthorsTotal()
    entries = ''
    for each in data_frame.authorName:
        entries = " ".join((entries, each.strip().replace(', ', '_').replace(' ', '_')))
    
    return entries

def cloud(cloudtext = "kw",
          grouper = 'paperID', 
          group = '', 
          outputFile = 'kwCloud.png', 
          grouped = False):
    '''
    : param cloudtext str : highlevel group inspecting ("kw" or "au")
    : param grouper str: column by which to group table by (i.e 'confName', 'pubYear')
    :       default 'paperID'
    : param group str/int: group to return results of (ie. 'ECSA', 'WICSA', 2009, 2014)
    :       default ''
    : param outputFile str: file to write image to, 
    :       default 'KWCloud.png'
    : grouped boolean : Boolean True if to render specified group (ie, conference or year)
    :       default False
    : output : WC
    '''
    print(cloudtext, grouper, group, outputFile, grouped)
    
    runcloud = {'kw' : prep_KWcloud(grouper, group, grouped),
                'au' : prep_Aucloud()
               }

    text = runcloud[cloudtext]

    #wc.generate(text)
    #Image from : https://lifebeinghusky.files.wordpress.com/2010/02/paw.jpg
    NortheasternHusky = np.array(Image.open("static/Images/paw.jpg"))
    
    # take relative word frequencies into account, lower max_font_size
    wc = WordCloud(background_color="white", 
                   max_font_size=40, 
                   relative_scaling=.5, 
                   mask=NortheasternHusky).generate(text)

    plt.figure()
    #plt.imshow(wc)
    plt.axis("off")
    #plt.show()
    # store Image?
    wc.to_file(outputFile)
    
    return wc
def cloud2(cloudtext = "kw",
          grouper = 'paperID', 
          group = '',  
          grouped = False):
    '''
    : param cloudtext str : highlevel group inspecting ("kw" or "au")
    : param grouper str: column by which to group table by (i.e 'confName', 'pubYear')
    :       default 'paperID'
    : param group str/int: group to return results of (ie. 'ECSA', 'WICSA', 2009, 2014)
    :       default ''
    : param outputFile str: file to write image to, 
    :       default 'KWCloud.png'
    : grouped boolean : Boolean True if to render specified group (ie, conference or year)
    :       default False
    : output : WC
    '''
    
    print(cloudtext, grouper, group, grouped)
    
    runcloud = {'kw' : prep_KWcloud(grouper, group, grouped),
                'au' : prep_Aucloud()
               }

    text = runcloud[cloudtext]
    print(text[0:50])
    #wc.generate(text)
    #Image from : https://lifebeinghusky.files.wordpress.com/2010/02/paw.jpg
    NortheasternHusky = np.array(Image.open("static/Images/paw.png"))
    
    # take relative word frequencies into account, lower max_font_size
    
    WordCloud( 
                   max_font_size=40, 
                   relative_scaling=.5, 
                   mask=NortheasternHusky).generate(text)

    
    plt.figure()
    #plt.imshow(wc)
    plt.axis("off")
    io = StringIO()
    plt.savefig(io, format='png')
    img = base64.encodestring(io.getvalue())
   
    io = StringIO()
    plt.savefig(io, format='png')
    data = base64.encodestring(io.getvalue())
    script = '''<img src="data:image/png;base64,{}";/>'''
    plt.close()
    return script.format(data)
