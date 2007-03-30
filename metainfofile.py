# Copyright 2007 Pieter Edelman (p _dot_ edelman _at_ gmx _dot_ net)
#
# This file is part of The Big Picture.
# 
# The Big Picture is free software; you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
# 
# The Big Picture is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
# 
# You should have received a copy of the GNU Lesser General Public License
# along with The Big Picture; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
# 

import byteform, datablock, qdb, types
   
class MetaInfoBlock:
  """ The base class for a particuler kind of metainformation structure, like
      Exif or IPTC info. This class provides the methods for searching over the
      different records for a specific tag. """
      
  def getTag(self, tag, record = None):
    """ Return the tag data with the specified number from the specified record.
    """
    
    # Get the record and tag numberss
    record_num, tag_num = self.__getRecordAndTagNum__(tag, record)
    
    # Get the data
    if (record_num):
      data = self.records.query("num", record_num, "record").getTagPayload(tag_num)
      return data
      
    return None
    
  def setTag(self, tag, payload, record = None):
    """ Set the specified tag in the specified record to the data, overriding
        all other occurences of that tag. If record num is omitted, the method
        will try to figure out which record is meant. """
        
    # Get the record and tag number
    rec_num, tag_num = self.__getRecordAndTagNum__(tag)
    
    # Set the data.
    if (rec_num):
      self.records.query("num", rec_num, "record").setTag(tag_num, payload)
  
  def __getRecordNum__(self, record):
    """ Return the record number based on a record number or name. """
    
    # Test numerical input
    if (type(record) == types.IntType):
      if record in self.records.getList("num"):
        return record
      else:
        raise ValueError, "Unknown record %d!" % record
    # Test text input
    elif (type(record) == types.StringType):
      index = self.records.getList("name", record)
      if (index):
        return self.records.query(index, "num")
      else:
        raise ValueError, "Unknown record %s!" % record
    else:
      raise TyepError, "I can't make sense of an record of type %s!" % type(record)

  def __getRecordAndTagNum__(self, tag, record = None):
    """ Return the record number and tag number for the supplied tag number or
        name in the specified record name or number. If record is omitted, the
        method will search in all records and raise an error if ambiguousnesses
        are found. """
      
    # If the user didn't specify a record, we search through all records
    if (record == None):
      records = self.records.getList("num")
    # Otherwise, we need to have a record number
    else:
      records = [self.__getRecordNum__(record)]

    # Find the possible records
    found_records = []
    for rec_num in records:
      tag_num = self.records.query("num", rec_num, "record").getTagNum(tag)
      if (tag_num is not False):
        found_records.append([rec_num, tag_num])

    # Warn if the tag occurs in multiple records
    if (len(found_records) == 0):
      raise KeyError, "Tag %s is unknown!" % str(tag)
    elif (len(found_records) > 1):
      raise "Tag %s occurs in multiple records!" % str(tag)
      
    return found_records[0]

class MetaInfoRecord(datablock.DataBlock):
  """ Base class for a metainformation record (like an IFD or an IPTC record). 
      Derived classes should hold create a QDB with the folowing lists:
      - name:      the tag names as strings
      - num:       the tag numbers as integers
      - count:     the number of words in each tag payload as integers or as
                   lists with the minimum and maximum count. None means that
                   this is undefined.
      - data_type: the data type as integer, or as a list of integers.
      The also should have a dict DATA_TYPES, coupling a data type number to
      a data type class.
  """
  
  def getTagNum(self, tag):
    """ Returns a tag number when fed a tag number or name, or False if it
        doesn't exist within the current record. """
    
    tag_num = False
    
    # Try numeric input
    if (type(tag) == types.IntType):
      if (self.records.query("num", tag)):
        tag_num = tag
    # Try text input
    elif (type(tag) == types.StringType):
      tag_num = self.records.query("name", tag, "num")
    else:
      raise TypeError, "Incorrect input type for finding tag numbers."
      
    return tag_num

  def getTagNums(self):
    """ Return a sorted list of set tag nums in this record. """
    
    tag_nums = self.fields.keys()
    tag_nums.sort()
    return tag_nums

  def hasTags(self):
    """ Return True if the record has any tags set, or False if not. """
    
    return (len(self.fields) > 0)

class MetaInfoFile:
  """The base class for files containing meta information."""
  
  def __init__(self):
    pass
    #self.ifds = dict.fromkeys(["tiff", "exif", "gps"], None)
    #self.iptc_info = None

  def getExifTagPayload(self, tag):
    """ Return the payload of a tag with the specified name. """
    
    payload = None
    
    # Iterate over all IFD's
    for ifd in ['tiff', 'exif', 'gps']:
      if (self.ifds[ifd]):
        payload = self.ifds[ifd].getTagPayload(tag)
        if payload:
          break

    return payload
    
  def getExifBlob(self, offset = 0):
    """ Return the encoded Tiff, Exif and GPS IFD's as a block. """
    
    if (self.exif):
      return self.exif.getBlob(offset)
    else:
      return None
    
  def getIPTCBlock(self):
    """ Return the encoded IPTC data as a blcok. """
    pass
