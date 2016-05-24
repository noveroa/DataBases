#!/usr/bin/python
#-*- coding: utf-8 -*-


import sys
import re
import pandas as pd

regXstripper = re.compile('[^a-zA-Z0-9]')
setLabels = ['affiliation', 'Source', 'Abstract', 'terms', 'Database', 'Classification Code']

def parseFile(input, Labels = setLabels):
    ''' Recast the abstract dictionary as a Pandas DataFrame
        : param input : .txt file from scientific abstracts 
        : param Labels : ['str']. List of only using pre-set labels to parse as strings.
                : default : ['title', 'authors', 'affiliation', 'Source', 'Abstract', 'terms', 'Database', 'code']
                
        : output : Python Dictionary of Dictionaries
                : primary key: value ===> abstractID : Python Dictionary
                : secondary key : value ===> abstractLabel : Datum
                
    '''
    i = 1
    abstracts = {}
    entry = {}
    terms = []
    
    with open(input, 'r+') as f:
        for line in f:
            if line[0].isdigit():
                #Only Title Lines Begin with Digit.
                entry['terms'] = terms
                abstracts[i-1] = entry
                entry = {}
                #Title Lines are followed by Authors
                idx, title = line.split('.', 1)
                entry['Title'] =  regXstripper.sub(' ', title).strip()
                i = int(idx) + 1
                authors =  f.next() 
                entry['Authors'] =  regXstripper.sub(' ', authors).strip()
                terms = []
            else:
                for c in Labels:
                    #error thrown as Compilation terms of Copyright lines being incorporated
                    if (c in line) and ('Compilation' not in line):
                        if ('terms' in line):
                            terms.append( line.split(':', 1)[1].strip())
                        else:
                            label, text = line.split(':', 1)
                            text = regXstripper.sub(' ', text)
                            label = regXstripper.sub(' ', label)
                            entry[label.strip()] = text.strip()
                    
                        
                    
                
    f.close()
    
    return abstracts

def makeAbstrDF(absDictionary, fname):
    ''' Recast the abstract dictionary as a Pandas DataFrame
        : param absDictionary : Python Dictionary of Dictionaries (see documentation above). 
            key: value ==> abstract idx (int) : abstract dictionary
        : output : Pandas DataFrame
            Given dictionary recast as dataframe with first row.  DataFrame Columns are Abstract Labels
    '''
    df = pd.DataFrame.from_dict(absDictionary, orient = 'index')
   
    df = df.drop(0, axis = 0)
    
    name = (fname.split('/')[-1]).strip('.txt')
    conf, year = name[:-4], name[-4:]
    df['Conf'] = conf
    df['year'] = year
    
    return df


def parseEntrytoDF(input):
    ''' Recast the abstract dictionary as a Pandas DataFrame
        : param input : .txt file from scientific abstracts 
            
        : output : Pandas DataFrame
            recast the file into a pandas DataFrame
    '''
    return makeAbstrDF(parseFile(input), input)