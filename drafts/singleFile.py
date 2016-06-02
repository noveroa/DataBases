#!/usr/bin/python
#-*- coding: utf-8 -*-


import sys
import re
import pandas as pd

regXstripper = re.compile('[^a-zA-Z]')


def parseFile(input):
    ''' Recast the abstract dictionary as a Pandas DataFrame
        : param input : .txt file from scientific abstracts 
                key: value ==> abstract idx (int) : (label, datum)
        : output : Python Dictionary
                recast the file into a pandas DataFrame
    '''
    f = open(input, "r")
    i = 1
    abstracts = {}
    entry = []
    for line in f:
        #Find An Abstract Instance, title
        if line[0].isdigit():
            abstracts[i-1] = entry
            entry = []
            entry.append((str(i), regXstripper.sub(' ', line).strip()))
            i = i + 1
        else:
        #A subcategory of the Abstract
            try:
                label, text = line.split(':', 1)
                text = regXstripper.sub(' ', text)
                label = regXstripper.sub(' ', label)
                entry.append((label.strip(), text.strip()))
            except:
                if line is None:
                    pass
                else:
                    text = regXstripper.sub(' ', line)
                    label = 'reparse'
                    entry.append((label, text.strip()))
                    
                
    f.close()
    return abstracts

def makeAbstrDF(absDictionary):
    ''' Recast the abstract dictionary as a Pandas DataFrame
        : param absDictionary : Python Dictionary. 
            key: value ==> abstract idx (int) : (label, datum)
        : output : Pandas DataFrame
            Given dictionary recast as dataframe with first row, 13th column
            dropped. Columns are set as labels
    '''
    df = pd.DataFrame.from_dict(absDictionary, orient = 'index')
    
    columns = [x[0] for x in df.iloc[1]]
    columns[0], columns[1], columns[11] = 'title', 'author', 'copyright'
    df = df.drop(13, axis =1)
    df = df.drop(0, axis = 0)
    df.columns = columns[:-1]
    
    return df

def parseEntrytoDF(input):
    ''' Recast the abstract dictionary as a Pandas DataFrame
        : param input : .txt file from scientific abstracts 
            
        : output : Pandas DataFrame
            recast the file into a pandas DataFrame
    '''
    return makeAbstrDF(parseFile(input))