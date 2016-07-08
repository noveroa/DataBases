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
from wordcloud import WordCloud, STOPWORDS#, ImageColorGenerator
import random


def prep_KWcloud():
    '''
    : param NONE
    : output : Returns a single string of keywords found in the given database.
    '''
    m, data_frame = flaskapp.getPapersKWgroup('paperID')
    entries = ""
    for each in data_frame.groups:
        
        entry = " ".join([key.replace (" ", "_") for key in data_frame.get_group(each)['keyword']])
        
        entries = " ".join((entries, entry))
    return entries

def KWcloud(outputfile = 'Images/pawtest.png'):
    '''
    : param NONE
    : output : Returns a saved .png file of the generated wordcloud.  Creating/saving
                a new image eachtime.
    
    '''
    #IF WANT TO ADD CERTAIN WORDS TO BE EXCLUDED>>>
    #stopwords = set(STOPWORDS)
    #stopwords.add("said")
    
    #generate a single string of ALL the keywords!
    text = prep_KWcloud()

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
    wc.to_file(outputfile)
    
    return wc

