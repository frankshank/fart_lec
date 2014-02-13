#!/usr/bin/env python

import xml.etree.ElementTree as ET
import localfeeds
import db

pois = []
for poi_type in db.Listings.types:
  feed_name = 'in/frommers-%s-local.xml' % poi_type
  print " ++ Parsing local feed '%s'" % feed_name
  pois.extend(localfeeds.parse_local_feed(xml=ET.parse(feed_name), type=poi_type))

# clear all old stuff from DB
db.clear_all()

print " >> Parsed a total of %d POIs" % len(pois)
db.save_pois(pois)
print " << Saved a total of %d POIs" % len(pois)
