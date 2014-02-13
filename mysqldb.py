#!/usr/bin/env python
"""MySQL DB library for reading contents of tcms_staging MySQL DB"""

import MySQLdb
import codecs

DB_USER='tcms_staging'
DB_PASS='tcms_staging'
DB_NAME='tcms_staging'
DB_PORT='3306'
DB_HOST='127.0.01'

DB_CONNECTION = MySQLdb.connect(host=DB_HOST, user=DB_USER, passwd=DB_PASS, db=DB_NAME,
    charset="utf8", use_unicode=True)

SQL = '''SELECT i.id, i.name, it.key_id, it.summary, it.description
  FROM onlineitemofinterest i, onlineitemofinteresttextualcontent it
  WHERE i.id = it.item_of_interest_id
  AND i.root_type_cd = 'POI'
  AND it.key_id IN ('FROMMERS')
'''

def db():
  "Connects to the MySQL DB and returns a cursor ready for action"
  return DB_CONNECTION.cursor()

def get_reviews():
  results = {}
  cur = db()
  cur.execute(SQL)
  print " >> Starting..."
  count = 0
  # process the row
  for id, name, key, summary, description in cur:
    count += 1    
    if summary is None and description is None:
      print " ++ ++ No textual content for %d - %s" % (id, key)
    else:
      if summary is not None:
        if description is not None:
          content = "%s %s" % (summary, description)
        content = summary
      else:
        content = description

      # remove any line breaks add the WOW review only if no Frommers one
      content = content.replace('\n', ' ')

      # Add new review
      if not id in results:
        results[id] = (key, content)
      # replace WHATSONWHEN review
      if id in results and results[id][0] == 'WHATSONWHEN':
        results[id] = (key, content)

  cur.close()
  DB_CONNECTION.close()
  print " << Done Loaded %d rows from DB" % count

  return results

if __name__ == '__main__':
  reviews = get_reviews()
  # Now dump revews out into a pipe separated file
  for key, value in reviews.iteritems():
    out.write('%d|%s\n' % (key, value[1]))
