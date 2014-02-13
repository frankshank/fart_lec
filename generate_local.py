#!/usr/bin/env python
"""Generate LEC XML for all POI types"""

import localfeeds
import db

from pprint import pprint

# load the list of mapped Listings
listings = db.Listings()

count = 0
for p_type in listings.types:

  # grab the POIS for a particular type
  pois   = listings.LISTINGS.get(p_type)
  p_list = [pois.get(key) for key in pois]

  localfeeds.generate_local_feed(p_list, p_type)
  count += len(pois)

print " ++ Done. Loaded %d pois" % count
