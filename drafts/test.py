
import re

file1 = 'ArchConfAbstracts/ECSA2007.txt'

def testme():
    f = open(file1, "r")
    test = open("test.txt", "w")
    i = 0
    abstracts = {}

    for line in f:
        if line[0].isdigit():
            print >> test, line,
            i=+1
            c= 0
            abstract= {}
            abstracts[i] = abstract
            abstract[c] = line
            
        else:
            c =+1
            abstract[c] = line
    
    return abstracts
           
