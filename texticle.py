#!/usr/bin/env python

import re

def de_cruft(txt):
  "TODO Remove all those double escaped tags"

def spacify(txt):
  "Replace </p><p> and </p> <p> With two unicode newlines"

  if txt is not None:
    return re.sub(r'</p>\s?<p>', '\\u000d\\u000d', txt)

def strip_spaces(txt):
  "De skenkify the text ie remove spaces and other pish"

  if txt is not None:
    return re.sub('\s\s+', ' ', txt)

def strip_tags(txt):
  "Remove HTML tags from supplied text"

  if txt is not None:
    return re.sub('<[^<]+?>', '', txt)

def sstrip(txt):
  "Remove HTML tags and double spaces, newlines etc"

  if txt is not None:
    txt = txt.replace('\n', '')
    txt = re.sub('<[^<]+?>', '', txt)
    txt = re.sub('\s\s+', ' ', txt)
    return txt

def nstrip(txt):
  "Remove HTML tags and double spaces but add newlines for end of paragraphs"

  if txt is not None:
    # add in the double line breaks in the paragraph breaks
    txt = re.sub(r'</p>\s?<p>', r'\n\n</p><p>', txt)
    txt = re.sub('<[^<]+?>', '', txt)
    return txt

def ustrip(txt):
  "Remove HTML tags and double spaces but add unicode newline \u000a for the end of paragraphs"

  if txt is not None:
    # add in the double line breaks in the paragraph breaks
    txt = re.sub(r'</p>\s?<p>', r'\u000a\u000a</p><p>', txt)
    txt = re.sub('<[^<]+?>', '', txt)
    return txt

def unify(txt):
  "Remove lines, add in double linebreaks, parse tags and return full unicode escaped string"

  if txt is not None:
    # add in the double line breaks in the paragraph breaks
    txt = re.sub(r'</p>\s?<p>', r'\u000a\u000a</p><p>', txt)
    # strip tags
    txt = re.sub('<[^<]+?>', '', txt)
    # strip rogue nbsp
    txt = txt.replace('&nbsp;', ' ')
    # strip duff escaped b, i and p tags
    txt = re.sub('&lt;/?[A-z]+&gt;', '', txt)
    # unicode escape all non-ascii characters
    txt = txt.encode('unicode-escape')
    # change hex code prefix to unicode one \x -> \u00
    txt = txt.replace('\\x', '\\u00')
    # replace double escapes
    txt = txt.replace(r'\\', '\\')
    # remove line breaks
    txt = txt.replace('\n', '')

    return txt

def utf8ify(txt):
  "Remove lines, add in double linebreaks (as \u000a\u000a) parse tags and return utf-8 encoded string"

  if txt is not None:
    # add in the double line breaks in the paragraph breaks
    txt = re.sub(r'</p>\s?<p>', r'\u000a\u000a</p><p>', txt)
    # strip tags
    txt = re.sub('<[^<]+?>', '', txt)
    # strip rogue nbsp
    txt = txt.replace('&nbsp;', ' ')
    # strip duff escaped b, i and p tags
    txt = re.sub('&lt;/?[A-z]+&gt;', '', txt)
    # remove line breaks
    txt = txt.replace('\n', '')
    # finally utf-8 encode
    txt = txt.encode('utf-8')

    return txt
