#!/usr/bin/python
# Copyright 2010 Google Inc.
# Licensed under the Apache License, Version 2.0
# http://www.apache.org/licenses/LICENSE-2.0

# Google's Python Class
# http://code.google.com/edu/languages/google-python-class/

import sys
import re


def read_file(filename):
  f=open(filename, 'r')
  f = f.readlines()
  return f

def unique_by_first_n(n, coll):
  seen = set()
  for item in coll:
    compare = tuple(item[:n])    # Keep only the first `n` elements in the set
    if compare not in seen:
      seen.add(compare)
      yield item

def extract_names(filename):
  """
  Given a file name for baby.html, returns a list starting with the year string
  followed by the name-rank strings in alphabetical order.
  ['2006', 'Aaliyah 91', Aaron 57', 'Abagail 895', ' ...]
  """
  # +++your code here+++
  f = open(filename, 'r')
  fl = read_file(filename)

  l = []
  lFiltFinal = []

  year_match = re.search(r'Popularity\sin\s(\d\d\d\d)', f.read())
  year = year_match.group(1)

  for line in fl:
    #if '<h3 align="center">Popularity in' in line:
      #year = line[-10:-6]
    if '<tr align="right"><td>' in line:
      rank = line[line.find('<td>')+len('<td>'):line.find('</td>')]
      boys = line[line.index('</td><td>')+len('</td><td>'):line.index('</td><td>',line.index('</td><td>')+1)]
      girls = line[line.index('</td><td>',line.index('</td><td>')+1)+len('</td><td>'):-6]
      l.append([boys,rank])
      l.append([girls,rank])

  lFilt = list(unique_by_first_n(1, l))

  lFiltFinal.append(year)
  for key in lFilt:
    lFiltFinal.append( key[0] + ' ' + key[1])

  lFiltFinal.sort()
  return lFiltFinal


def main():
  # This command-line parsing code is provided.
  # Make a list of command line arguments, omitting the [0] element
  # which is the script itself.
  args = sys.argv[1:]

  if not args:
    print('usage: [--summaryfile] file [file ...]')
    sys.exit(1)

  # Notice the summary flag and remove it from args if it is present.
  summary = False
  if args[0] == '--summaryfile':
    summary = True
    del args[0]

  # +++your code here+++
  # For each filename, get the names, then either print the text output
  # or write it to a summary file
  for filename in args:
    myList = extract_names(filename)

    if summary == True:
      text = '\n'.join(myList) + '\n'
      f=open(filename + '.summary', 'w')
      f.write(text)
      f.close()
    #print(text)
    else:
      print(myList)
  
if __name__ == '__main__':
  main()
