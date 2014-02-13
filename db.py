#!/usr/bin/env python
"""SQLite DB library utilities for the Frommers local feed parser"""

import sqlite3

DB_FILE='sql/listings.sqlite'

def clear_all():
  "Clears all the DB listings and associated tables"

  with sqlite3.connect(DB_FILE) as conn:
    c = conn.cursor()

    c.execute("DELETE FROM listings") 
    print " ++ Deleted listings..."
  
    c.execute("DELETE FROM addresses") 
    print " ++ Deleted addresses..."
  
    c.execute("DELETE FROM categories") 
    print " ++ Deleted categories..."
  
    c.execute("DELETE FROM attributes") 
    print " ++ Deleted attributes..."
  
    c.execute("DELETE FROM images") 
    print " ++ Deleted images..."
  
    c.execute("DELETE FROM phones") 
    print " ++ Deleted phones..."
  
def reviews():
  "Grabs all the reviews with their associated ids "

  with sqlite3.connect(DB_FILE) as conn:
    c = conn.cursor()

    reviews = list(c.execute("SELECT id, content FROM listings WHERE content != ''"))
    print " ++ loaded %d reviews" % len(reviews)

  return reviews

def save_pois(listings):
  "Saves a list of POI objects when the list contains each poi as a dict"

  pois      = []
  atts      = []
  phones    = []
  cats      = []
  images    = []
  addresses = []
  
  for poi in listings:
    # append the POI listing
    pois.append(poi.as_tuple())

    # add the multis
    atts.extend(poi.atts())
    phones.extend(poi.phones())
    cats.extend(poi.cats())
    images.extend(poi.images())
    addresses.extend(poi.adds())

  with sqlite3.connect(DB_FILE) as conn:
    c = conn.cursor()

    c.executemany("""INSERT INTO listings (
      id, 
      type,
      name,
      country,
      review_type,
      link,
      content,
      rating,
      website,
      email,
      address_format,
      longitude,
      latitude
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", pois)
    conn.commit()
    print " ++ Loaded a total of %d listings" % c.rowcount

    # addresses
    c.executemany("""INSERT INTO addresses (
      listing_id, 
      name,
      value
    ) VALUES (?, ?, ?)""", addresses)
    conn.commit()
    print " ++ Loaded a total of %d addresses" % c.rowcount

    # telephone nums
    c.executemany("""INSERT INTO phones (
      listing_id, 
      type,
      value
    ) VALUES (?, ?, ?)""", phones)
    conn.commit()
    print " ++ Loaded a total of %d phone numbers" % c.rowcount

    # attributes
    c.executemany("""INSERT INTO attributes (
      listing_id, 
      name,
      value
    ) VALUES (?, ?, ?)""", atts)
    conn.commit()
    print " ++ Loaded a total of %d attributes" % c.rowcount

    # categories
    c.executemany("""INSERT INTO categories (
      listing_id, 
      value
    ) VALUES (?, ?)""", cats)
    conn.commit()
    print " ++ Loaded a total of %d categories" % c.rowcount

    # images
    c.executemany("""INSERT INTO images (
      listing_id, 
      type,
      title,
      author,
      url,
      width,
      height
    ) VALUES (?, ?, ?, ?, ?, ?, ?)""", images)
    conn.commit()
    print " ++ Loaded a total of %d images" % c.rowcount

def update_review(id, content):
  """update the content for a listing based on a particular id"""
  with sqlite3.connect(DB_FILE) as conn:
    c = conn.cursor()
    c.execute("UPDATE listings SET content = ? WHERE id = ?", (content, id))
    conn.commit()

    print " ++ Updated review content for listing id:", id

# The entire POI Listings
class Listings:
  """The class containing all the DB tables loaded into memory"""

  # allowed POI types
  types = ('SHOPPING', 'HOTEL', 'NIGHTLIFE', 'ATTRACTION', 'RESTAURANT')

  poi_type_lookup = dict()

  # all the POIS sorted by type
  LISTINGS = dict(
      SHOPPING   = dict(),
      NIGHTLIFE  = dict(),
      RESTAURANT = dict(),
      ATTRACTION = dict(),
      HOTEL      = dict()
  )

  def __init__(self):
    print " ++ Loading DB data for Listings..."

    # load up everything on one shot rather than multi row pish
    with sqlite3.connect(DB_FILE) as conn:
      conn.row_factory = sqlite3.Row

      # addresses
      add_cur = conn.cursor()
      addresses_list = list(add_cur.execute("SELECT * FROM addresses"))
     
      # phones
      phone_cur = conn.cursor()
      phone_list = list(phone_cur.execute("SELECT * FROM phones"))
     
      # categories
      cat_cur = conn.cursor()
      categories_list = list(cat_cur.execute("SELECT * FROM categories"))
    
      # attributes
      att_cur = conn.cursor()
      attributes_list = list(cat_cur.execute("SELECT * FROM attributes"))
    
      # images
      img_cur = conn.cursor()
      images_list = list(cat_cur.execute("SELECT * FROM images"))

      # listings
      c = conn.cursor()
      listings_list = list(c.execute("SELECT * FROM listings"))
    
    # Add each Poi to the correct POI type dict
    for l in listings_list:
      type_key = l['type']
      poi_id   = l['id']
      poi      = Poi(l)

      # add an entry to the poi_type lookup table
      self.poi_type_lookup[poi_id] = type_key

      # and add our fully populated self to the relevant type
      self.LISTINGS[type_key][poi_id] = poi

    # decode addresses
    for add in addresses_list:
      l_id    = add['listing_id']
      add_key = add['name']
      add_val = add['value']
      p_type  = self.poi_type_lookup[l_id] 

      self.LISTINGS[p_type][l_id].add_address(add_key, add_val)

    # decode phones
    for p in phone_list:
      l_id   = p['listing_id']
      p_key  = p['type']
      p_val  = p['value']
      p_type = self.poi_type_lookup[l_id] 

      self.LISTINGS[p_type][l_id].add_phone(p_key, p_val)

    # decode categories
    for c in categories_list:
      l_id   = c['listing_id']
      c_val  = c['value']
      p_type = self.poi_type_lookup[l_id] 

      self.LISTINGS[p_type][l_id].add_category(c_val)

    # decode attributes
    for a in attributes_list:
      l_id   = a['listing_id']
      a_key  = a['name']
      a_val  = a['value']
      p_type = self.poi_type_lookup[l_id] 

      self.LISTINGS[p_type][l_id].add_attribute(a_key, a_val)

    # decode images
    for i in images_list:
      l_id   = i['listing_id']
      p_type = self.poi_type_lookup[l_id] 

      self.LISTINGS[p_type][l_id].add_image(
        title  = i['title'],
        author = i['author'],
        url    = i['url'],
        width  = i['width'],
        height = i['height']
      )

    print " ++ Successfully loaded %d POI types into our master Listings" % len(self.LISTINGS)
      
# POI class
class Poi:
  "The single POI Listing class"
  
  def __init__(self, row):

    poi_id   = row['id']
    if not poi_id:
      raise Exception("No ID supplied for POI listing")

    poi_type = row['type']

    if poi_type not in Listings.types:
      raise Exception("Unknown listing type: %s" % poi_type)

    "Initialize Poi from a dict"
    self.id             = poi_id
    self.type           = poi_type
    self.name           = row['name']
    self.country        = row['country']
    self.review_type    = row['review_type']
    self.link           = row['link']
    self.content        = row['content']
    self.rating         = row['rating']
    self.website        = row['website']
    self.email          = row['email']
    self.longitude      = row['longitude']
    self.latitude       = row['latitude']
    self.address_format = 'simple'
    self.attributes     = []
    self.categories     = []
    self.addresses      = []
    self.phone_nums     = []
    self.imgs           = []

  def __str__(self):
    return "ID:%d - '%s'" % (self.id, self.name.encode('utf-8'))

  def add_attribute(self, key, value):
    self.attributes.append(dict(
      key   = key,
      value = value
    ))

  def add_phone(self, type, tel):
    self.phone_nums.append(dict(
      type  = type,
      value = tel
    ))

  def add_address(self, name, val):
    self.addresses.append(dict(
      name  = name,
      value = val
    ))

  def add_category(self, c):
    self.categories.append(c)

  def add_image(self, **img):
    self.imgs.append(dict(
      title  = img.get('title'),
      author = img.get('author'),
      url    = img.get('url'),
      width  = img.get('width'),
      height = img.get('height')
    ))

  def as_tuple(self):
    return (
      self.id,
      self.type,
      self.name,
      self.country,
      self.review_type,
      self.link,
      self.content,
      self.rating,
      self.website,
      self.email,
      self.address_format,
      self.longitude,
      self.latitude,
    )

  def atts(self):
    return [(self.id, a['key'], a['value']) for a in self.attributes]

  def cats(self):
    return [(self.id,  c) for c in self.categories]

  def phones(self):
    return [(self.id, p['type'], p['value']) for p in self.phone_nums]

  def images(self):
    return [(self.id, 'photo', i['title'], i['author'], i['url'], i['width'], i['height']) for i in self.imgs]

  def adds(self):
    return [(self.id, a['name'], a['value']) for a in self.addresses]
