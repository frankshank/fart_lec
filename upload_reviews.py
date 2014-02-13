#!/usr/bin/env python
"""reads a list of reviews in pipe delimited format with id|content and loads em"""
import db
import codecs

with codecs.open('sql/wow_concatenated_reviews.lst', 'rU', 'utf-8') as f:
  for i, line in enumerate(f):
    line = line.strip()
    tokens = line.split('|')
    id = tokens[0]
    txt = tokens[1].encode('ascii', 'xmlcharrefreplace')

    print " ++ {0} Updating listing id: {1} - {2}".format(i, id, txt)
    db.update_review(id, txt)

print " ++ Done updating reviews"
