#!/usr/bin/python
#-*- coding: utf-8 -*-
import sys, os
import pandas as pd
import numpy as np
import math, operator, random, warnings
warnings.filterwarnings('ignore')
import requests
import json

def tenizenQ():
    print('''WELCOME!!!!!!
            Author: Aileen Novero
            Purpose: My attempt at the Tenizen Interview Questions.
            Result: learning and fun!  
            Caveat: There is hard-coded variables.  One could change this or perhaps eschew the data_frame 
                idea and create tuples from the csv.  Yet this made most sense with Python.
                Though python is OOP, I did not utilize classes.
            Language:
                Python.  I utilized python as I am most familiar with it.  The packages include pandas 
                which is helpful in manipulating different inputs, ie a csv and a json call.         
                It is an easier syntax to read and understand.
                Also, it is based on dictionaries just like json! which allows for easier converting
                between the two.
                Further, it can easily be used to create stats. Like pd.describe(). Or visualizations
                However, it does have limits - it can be slow and has size limitations (especially with 
                recursive functions
                
            Functions: 
                getaptTable : controls which dataset to parse
                jsonMoreApts : runs json query
                coordDistance : returns distance in miles between two coordinates
                findDistances : returns a distance and two apt idx based on query/operator
                    findMax : runs findDistance with operator.gt
                    findMin : runs findDistance with operator.lt 
                findGraniteApts : returns number of apts with granite countertops under(and including) 
                            a random price point
                bestSqFtPrice : returns aptIdx and sqftprice of apt meeting noted requirements 
            To run:
                sysarg[1] is function call
                sysarg[2] is the dataset to run (either 'getMore' or anything of your fancy) 
        ''')


''' Helper functions for controlling which data set to use:
    Use 'getMoreApts' as command line parameter to run utilizing json query apts 1001, 1050
    Else runs first call of 0-1000 apts
    '''

def getaptTable(entry):
    '''
    : param entry : Control string for which data set to use. For apts idx 1001-1050, use
                    'getMore'
    : returns the pandas dataframe corresponding to the dataset
    '''
    if entry == 'getMore':
        return jsonMoreApts()
    else:
        return pd.DataFrame.from_csv('apartments.csv')
    
def jsonMoreApts(param1 = 1001, param2 = 1050):
    '''
    : param param1 : int. Starting apartment index of json query
    : param param2 : int. Ending apartment index of json query
    : returns the pandas dataframe corresponding to the dataset
    '''
    #json request
    headers = {'content-type': 'application/json'}
    url = 'http://52.201.94.104:8080'
    params = {'first_id': str(param1), 'last_id': str(param2)}
    r = requests.post(url, params=params, headers = headers).text
    
    #to Pandas!
    pdJson = pd.read_json(r)
    pdJson.set_index('Id', inplace= True)
    pdJson.Amenities = pdJson.Amenities.apply(lambda am: str(am).strip('[]').replace("'", '|'))
    return pdJson

''' Initialize global variables:
    aptTable : python pandas dataframe. json call or csv converted to pandas dataframe.
             : columns = 
            '''
aptTable = getaptTable(sys.argv[2])

'''aptTable['coordinates']: column grouping lat/long into a column of tuples'''
aptTable['coordinates'] = aptTable.apply(lambda x: [x['Latitude'], x['Longitude']], axis=1) 

'''coordinates: casting coordinates column to numpy array'''
coordinates = np.array(aptTable.coordinates)


#FROM : https://gist.github.com/rochacbruno/2883505
#helper function
def coordDistance(origin, destination):
    '''
    : param origin : Tuples of Floats. Tuples are the latitude, longitude coordinates. 
    : param destination : Tuples of Floats. Tuples are the latitude, longitude coordinates. .
    
    : returns the Maximum/Min distance (in miles, as designated) between two apartments, 
                   and the given apts indices
    '''
    lat1, lon1 = origin
    lat2, lon2 = destination
    radius = 3956 #miles

    dlat = math.radians(lat2-lat1)
    dlon = math.radians(lon2-lon1)
    a = math.sin(dlat/2) * math.sin(dlat/2) + math.cos(math.radians(lat1)) \
        * math.cos(math.radians(lat2)) * math.sin(dlon/2) * math.sin(dlon/2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    d = radius * c

    return d

def findDistances(coords, limit, op):
    '''
    : param coords : numpy array of tuples. Tuples are the latitude, longitude coordinates. 
    : param limit  : real.  Number representing the control limit for finding min/max distance.
    : param op     : python operator. ie, operator.gt, operator.lt
    : returns the Maximum/Min distance (in miles, as designated) between two apartments, 
                   and the given apts indices
    : ****NOTE!!  The runTime is NOT terribly great, with two(!) for loops nested... :(****
    '''
    aptIndex = []
    curLimit =  limit
    
    for i,c1 in enumerate(coords):
        for j,c2 in enumerate(coords[i:]):
            if i != j+i:
                distance = coordDistance(c1,c2)
                if op(distance, curLimit):
                    curLimit = distance
                    aptIndex = (i, j+i)
    return curLimit, aptIndex


def findMax(coords = coordinates, indices = np.array(aptTable.index)):
    '''
    : param coords : numpy array of tuples. Tuples are the latitude, longitude coordinates. 
                   : defaults to np.array(aptTable.coordinates)
    : returns the Maximum distance (in miles) between two apartments, and the given apts indices
    '''
    
    miles, aptIdx =   findDistances(coords, limit = -1, op = operator.gt)
    
    #to ensure correct index from original dataset
    idx = (indices[aptIdx[0]], indices[aptIdx[-1]])
    
    print('Maximum distances: %.2f Apartment Ids: %s')%(miles, idx)
    return miles, idx


def findMin(coords = coordinates, indices = np.array(aptTable.index)):
    '''
    : param coords : numpy array of tuples. Tuples are the latitude, longitude coordinates. 
                   : defaults to np.array(aptTable.coordinates)
    : returns the Minimum distance (in miles) between two apartments, and the given apts indices
    '''
    miles, aptIdx =  findDistances(coords, limit = np.Inf, op = operator.lt)
    #to ensure correct index from original dataset
    idx = (indices[aptIdx[0]], indices[aptIdx[-1]])
    
    print('Minimum distances: %.2f Apartment Ids: %s')%(miles, idx)
    return miles, idx

'''Problem 2
   Find the min and max rents.
   Choose a random integer in that range (inclusive), then find the number of apartments 
   at that price or less that have Granite Countertops.
    '''
def findGraniteApts(data_frame = aptTable):
    '''
    : param data_frame: Python Pandas DataFrame, python structure with columns Amenities
                        as described in aptTable definition.  
                      : defaults to aptTable
    : returns the number of apartments with Granite Countertops under a random number (inclusive)
    '''
    r = random.randrange(min(data_frame.Price), max(data_frame.Price)+1)
    print('Returned Apts under $%d')%r
    df = data_frame[data_frame['Price'] <= r][data_frame['Amenities'].str.contains('Granite Countertops')==True]
    print('Number of relevant apts: %d')%len(df)
    return len(df)


''' Problem 3
    A friend wants an apartment with Central Air and at least three other amenities. 
    Which apartment fulfilling these criteria has the best price per square foot and 
    what is it, rounded to the nearest cent?
    ***Assumption Made: assuming the 'best price' is that which is the minimum price/sqft
    '''
def bestSqFtPrice(data_frame = aptTable):
    '''
    : param data_frame: Python Pandas DataFrame, python structure with columns Amenities and SqFtPrice
                        as described in aptTable definition.  
                      : defaults to aptTable
    : returns the apartment index and price per square foot of apartment (to nearest cent) with 
                        'Best SqFt Value' meeting requirments: Central Air and >= 3 other Amernities
    '''
    centralAir = data_frame[data_frame['Amenities'].str.contains('Central Air')==True]
    centralAir['AmentityCounts'] = centralAir['Amenities'].apply(lambda a: len(a.split('|')))
    centralAir.query('AmentityCounts >= 4', inplace = True)
    centralAir['SqFtPrice'] = centralAir.Price/centralAir['Square footage']
    aptidx = centralAir['SqFtPrice'].idxmin()
    bestPrice = min(centralAir.SqFtPrice)
    assert centralAir.loc[aptidx].SqFtPrice == bestPrice
    
    print('Desired Apt: %d at sqftValue: %.2f $/sqft')%(aptidx, bestPrice)
    return aptidx, bestPrice

if __name__ == '__main__':
    globals()[sys.argv[1]]()
    filename = sys.argv[2]