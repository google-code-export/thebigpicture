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
   
class MetaInfoBlock(datablock.DataBlock):
   
##  def __init__(self):
##    """ Placeholder. Wrapper functions should override this. """
##    
##    # Derived classes should override this
##    self.records = qdb.QDB()
    
  def getTag(self, tag, record = None):
    """ Return the tag data with the specified number from the specified record.
    """
    
    # Get the record and tag nums
    record_num, tag_num = self.__getRecordAndTagNum__(tag, record)

    if (record_num):
      data = self.records.query("num", record_num, "record").getTagPayload(tag_num)
      return data
    return None
    
  def setTag(self, tag, payload, record = None):
    """ Set the specified tag in the specified record to the data, overriding
        all other occurences of that tag. If record num is omitted, the method
        will try to figure out which record is meant. """
        
    rec_num, tag_num = self.__getRecordAndTagNum__(tag)
    if (rec_num):
      self.records.query("num", rec_num, "record").setTag(tag_num, payload)

##  def appendTag(self, tag, payload, record = None):
##    """ Append the specified tag in the specified record to the data. """
##    
##    rec_num, tag_num, tag = self.__getSetData__(tag, payload, record = record)
##    if (tag):
##      self.records[rec_num].appendTag(tag_num, tag)
  
##  def encode(self, rec_num, tag_num, payload):
##    """ Encode the data according to the specifications of the tag. """
##    
##    # Try to encode the tag
##    record = self.records.query("num", rec_num, "table")
##    data_types = record.getDataType(tag_num)
##    if (data_types != None):
##      # Try to encode the data with each of the possible data types. Stop when
##      # we succeeded.
##      if (type(data_types) != types.ListType):
##        data_types = [data_types]
##        
##      success = False
##      for data_type in data_types:
##        try:
##          data = self.DATA_TYPES[data_type].encode(payload, self.big_endian)
##          success = True
##        except:
##          pass
##        if (success):
##          break
##    else:
##      # If we don't have a data type, raise an error
##      raise "Setting tag %s is not implemented!" % str(tag)
##    
##    # Check for the proper length
##    
##    # Retrieve the allowed lengths
##    word_width = self.DATA_TYPES[data_type].word_width
##    count = record.getCount(tag_num)
##    if (type(count) == types.ListType):
##      min_length = count[0] * word_width
##      max_length = count[1] * word_width
##    else:
##      min_length = count * word_width
##      max_length = None
##      
##    # Check lengths
##    if (len(data) < min_length) or ((max_length != None) and (len(data) > max_length)):
##      raise ValueError, "Encoded data takes %d bytes, while only %d bytes are allowed!" % (len(data), max_length)
##    
##    return data

##  def decode(self, tag, data, big_endian = True):
##    """ Encode the data according to the specifications of the tag. """
##    
##    record_num, tag_num = self.__getRecordAndTagNum__(tag)
##    data_type = self.records.query("num", record_num, "record").getDataType(tag_num)
##    payload = self.DATA_TYPES[data_type].decode(data, is_big_endian = self.big_endian)
##    return payload

  def __getRecordNum__(self, record):
    """ Returns the record number based on a record number or name. """
    
    # Test numerical input
    if (type(record) == types.IntType):
      if record in self.records.getList("num"):
        return record
      else:
        raise "Unknown record %d!" % record
    # Test text input
    elif (type(record) == types.StringType):
      if (record in self.records.getList("name")):
        return self.records.query("name", record, "num")
      else:
        raise "Unknown record %s!" % record
    else:
      raise "I can't make sense of an record of type %s!" % type(record)

  def __getRecordAndTagNum__(self, tag, record = None):
    """ Return the record number and tag number for the supplied tag number or
        name in the specified record name or number. If record is omitted, the
        method will search in all records and raises an error if doubles are
        found. """
      
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

  def __getSetData__(self, tag, payload, record = None):
    """ Return the record number, tag number, and DataBlock object for numeric
        or name inputs. This method is used by the setTag and appendTag methods.
    """
        
    # Get the record and tag number
    rec_num, tag_num = self.__getRecordAndTagNum__(tag, record)
    
    if ((rec_num != None) and (tag_num != None)):
      # Encode the data
      data = self.encode(rec_num, tag_num, payload)
      tag = datablock.DataBlock(data = data)
    else:
      raise "No valid destination could be found for tag %s" % str(tag)
  
    return [rec_num, tag_num, tag]

class RecordInfo(qdb.QDB):
  """ Base class for retrieving data about tags in IPTC records. Derived
      classes should implement the following lists:
      - name : the names of the tags
      - num  : the numbers of the tags
      - count: the number of words every tag should occupy, with None
                    to indicate that this is free
      - type : the numbers of tag data types of the tags, as found in
                iptcdatatypes.TYPES
  """
  
  def getTagNum(self, tag):
    """ Returns a tag number when fed a tag number or name, or None if it
        doesn't exist within the current record. """
        
    ret = None
    
    if (type(tag) == types.IntType):
      # We have a tag number as user input
      if tag in self.num:
        ret = tag
    elif (type(tag) == types.StringType):
      # We have a tag name, search the number for it
      try:
        ret = self.query("name", tag, "num")
      except ValueError:
        pass
  
    return ret

  def getDataType(self, tag):
    """ Return the data type for a certain tag (name or number). """
    tag_num   = self.getTagNum(tag)
    data_type = self.query("num", tag_num, "data_type")
    return data_type

  def getCount(self, tag):
    """ Return the count for a certain tag (name or number), if any, or None
        if otherwise. """
    tag_num = self.getTagNum(tag)
    return self.query("num", tag_num, "count")

  def encode(self, tag, payload, big_endian = True):
    """ Encode the data according to the specifications of the tag. """
    
    # Try to encode the tag
    index = self.query("num", self.getTagNum(tag))
    data_type = self.query(index, "data_type")
    if (data_type != None):
      data = self.DATA_TYPES[data_type].encode(payload, is_big_endian = big_endian)
    else:
      # If we don't have a data type, raise an error
      raise "Setting tag %s is not implemented!" % str(tag)
    
    # Check for the proper length
    
    # Retrieve the allowed lengths
    word_width = self.DATA_TYPES[data_type].word_width
    count = self.query(index, "count")
    if (type(count) == types.ListType):
      min_length = count[0] * word_width
      max_length = count[1] * word_width
    else:
      min_length = count * word_width
      max_length = None
      
    # Check lengths
    if (len(data) < min_length):
      # If data type is Digits, pad it with zeroes
      if (data_type == 15):
        data = (min_length - len(data)) * "0" + data
    elif (max_length != None) and (len(data) > max_length):
      raise "Encoded data takes %d bytes, while only %d bytes are allowed!" % (len(data), max_length)
    
    return data

  def decode(self, tag, data, big_endian = True):
    """ Encode the data according to the specifications of the tag. """
    tag_num   = self.getTagNum(tag)
    data_type = self.query("num", tag_num, "data_type")
    payload   = iptcdatatypes.TYPES[data_type].decode(data, is_big_endian = big_endian)
    return payload
    
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
