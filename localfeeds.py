#!/usr/bin/env python

from xml.etree import ElementTree
from xml.dom import minidom
from xml.etree.ElementTree import Element, SubElement, Comment

import texticle as text

# lookup for the main category
types = dict(
  RESTAURANT = 'Restaurants',
  SHOPPING   = 'Shops',
  NIGHTLIFE  = 'Nightlife',
  ATTRACTION = 'Attractions',
  HOTEL      = 'Hotels',
)

def parse_local_feed(**k):
  "Parses the Frommers POI feed"

  xml  = k.get('xml')
  type = k.get('type')

  # container for our POIs
  pois = []

  # loop through all the listing entries
  count = 0
  for listing in xml.iter('listing'):

    # initialise our listing
    poi_id = int(listing.findtext('id'))
    l = dict(id=poi_id, type=type)

    # listing name
    l['name'] = listing.findtext('name')

    # country code
    l['country'] = listing.findtext('country')
  
    # lat and lng
    lat = listing.findtext('latitude')
    lng = listing.findtext('longitude')

    if lat is not None:
      l['latitude'] = float(lat)
    if lng is not None:
      l['longitude'] = float(lng)

    # content tag
    content = listing.find('content')

    # review details (content/review)
    review = content.find('review')
    l['review_type'] = review.get('type')

    l['link']    = text.sstrip(review.findtext('link'))
    l['rating']  = review.findtext('rating')

    # strip tags from cleaned review text
    l['content'] = text.sstrip(review.findtext('body'))

    # content/attributes
    content_atts = content.find('attributes')
    if content_atts is not None:
      # website
      website = content_atts.findtext('website')
      if website is not None:
        l['website'] = website

      # email
      email = content_atts.findtext('email')
      if email is not None:
        l['email'] = email

    # now we have all our props, create the POI
    poi = Poi(l)

    # phone numbers
    for p in listing.iter('phone'):
      poi.add_phone(p.get('type'), p.text)

    # address components (note here we always assume addresses are of format = 'simple' 
    add = listing.find('address')
    if add is not None:
      [poi.add_address(c.get('name'), s(c.text)) for c in add.iter('component') if c.text is not None]

    # images 
    for img in listing.iter('image'):
      # print " ++ Checking image:%s author:%s" % (img.get('url'), img.findtext('title'))
      poi.add_image(
        title  = text.sstrip(img.findtext('title')),
        author = text.sstrip(img.findtext('author')),
        url    = img.get('url'),
        width  = img.get('width'),
        height = img.get('height')
      )

    # categories 
    for cat in listing.iter('category'):
      poi.add_cat(s(cat.text))

    # Grab the child atts of attributes tag
    for a in content.iter('attr'):
      if a.text is not None:
        a_tag = a.tag
        a_key = a.get('name')
        a_val = text.sstrip(a.text)
        poi.add_attr(a_key, a_val)

    count += 1
    print " ++ %s ++ Loading id:%d '%s'" % (count, poi_id, l.name)
    pois.append(l)

  return pois

# generate local XML
def generate_local_feed(poi_list, poi_type):
  "Given a list of POIs generated the Frommers LEC feed for this type"

  # declare our root element
  root = Element('listings', {
    'xmlns:xsi'                     : 'http://www.w3.org/2001/XMLSchema-instance',
    'xsi:noNamespaceSchemaLocation' : 'http://local.google.com/local_feed.xsd'
  })

  # lang
  id = SubElement(root, 'language')
  id.text = 'en'

  # datum
  name = SubElement(root, 'datum')
  name.text = 'WGS84'
    
  # only bother about POIs that have content
  pois = [poi for poi in poi_list if len(poi.content) > 0]

  for p in pois:
    listing = SubElement(root, 'listing')

    # id
    id = SubElement(listing, 'id')
    id.text = str(p.id)

    # name
    name = SubElement(listing, 'name')
    name.text = text.sstrip(p.name)

    # addresses
    address = SubElement(listing, 'address', {'format': 'simple'})
    for add in p.addresses:
      component = SubElement(address, 'component', {'name': add.get('name') })
      component.text = add.get('value')

    # country
    country = SubElement(listing, 'country')
    country.text = p.country

    # latitude
    lat = SubElement(listing, 'latitude')
    lat.text = str(p.latitude)

    # longitude
    lng = SubElement(listing, 'longitude')
    lng.text = str(p.longitude)

    # phone_nums
    for phone in p.phone_nums:
      tel = SubElement(listing, 'phone', {'type': phone.get('type')})
      tel.text = phone.get('value')

    # categories
    for c in p.categories:
      cat = SubElement(listing, 'category')
      cat.text = c

    # content
    content = SubElement(listing, 'content')

    # content/review
    review = SubElement(content, 'review', {'type': 'editorial'})
    # link
    if p.link is not None:
      review_link = SubElement(review, 'link')
      review_link.text = p.link
    # rating
    if p.rating is not None:
      rating = SubElement(review, 'rating')
      rating.text = str(p.rating)
    # body
    if p.content is not None:
      body = SubElement(review, 'body')
      body.text = text.ustrip(p.content)

    # content/attributes
    atts = SubElement(content, 'attributes')
    if len(p.email) > 0:
      email = SubElement(atts, 'email')
      email.text = (p.email)
    if len(p.website) > 0:
      website = SubElement(atts, 'website')
      website.text = (p.website)
    # generic atts 
    for a in p.attributes:
      att = SubElement(atts, 'attr', {'name': a.get('key')})
      att.text = text.sstrip(a.get('value'))

    # content/images
    for img in p.imgs:
      image = SubElement(content, 'image', {
        'type'   : 'photo',
        'url'    : img.get('url'),
        'width'  : str(img.get('width')),
        'height' : str(img.get('height'))
      })
      image_link = SubElement(image, 'link')
      image_link.text = img.get('url')
      # image/title
      if img.get('title') is not None:
        image_title = SubElement(image, 'title')
        image_title.text = img.get('title')
      # image/author
      if img.get('author') is not None:
        image_author = SubElement(image, 'author')
        image_author.text = img.get('author')

  # clean up formatting of final XML string
  # txt = prettify(root)
  txt = ElementTree.tostring(root)

  feed_name = 'out/frommers-%s-local.xml' % poi_type
  f = open(feed_name, 'w')
  # f.write(txt.encode('ascii', 'xmlcharrefreplace'))
  f.write(txt.encode('unicode-escape').replace('\\x', '\u00').replace(r'\\', '\\').replace(r'\\n', '\n'))
      
  print " ++ generated LEC xml for %d POIs of type %s" % (len(pois), poi_type)

def prettify(elem):
    "Return a pretty-printed XML string for the Element"
    rough_string = ElementTree.tostring(elem)
    reparsed = minidom.parseString(rough_string)

    return reparsed.toprettyxml(indent="  ")
