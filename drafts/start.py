#!/usr/bin/python
#-*- coding: utf-8 -*-
import sys

def printFileName(filename):
  print filename

def main():
  args = sys.argv[1:]
  for filename in args:
    printFileName(filename)

if __name__ == '__main__':
  main()
#Then from the console, you can start it like that :

#python MyScript.py /home/andy/tmp/1/*.txt /home/andy/tmp/2/*.html