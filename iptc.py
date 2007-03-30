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

# Import standard Python modules
import types
# Import custom modules
import byteform, datablock, datatypes, metainfofile, qdb

# === Stuff relating to the IPTC data types ===
class Digits(datatypes.DataType):
  """ The digits data type is a kind of ASCII data which only accepts numbers.
  """
  word_width = 1
  
  @classmethod
  def encode(cls, num, is_big_endian = True):
    """ Encode an integer number as string. """

    if (num in [types.ListType, types.TupleType]):
      num = [num]
    
    return str(num)
    
  @classmethod
  def decode(cls, byte_stream, is_big_endian = True):
    """ Convert a string of numbers to a list containing a single number. """
        
    return [int(byte_stream)]
    
# NOTE: These aren't "official" data type numbers.
DATA_TYPES = {
  1: datatypes.Byte,
  2: datatypes.Ascii,
  3: datatypes.Short,
  4: datatypes.Long,
  5: datatypes.Rational,
  7: datatypes.Undefined,
  15: Digits
} 

class IPTCRecord(metainfofile.MetaInfoRecord):
  """ Base class for retrieving data about tags in IPTC records. Derived
      classes should implement the following lists:
      - name : the names of the tags
      - num  : the numbers of the tags
      - count: the number of words every tag should occupy, with None
                    to indicate that this is free
      - type : the numbers of tag data types of the tags, as found in
                DATA_TYPES
  """
  
  def __init__(self, **kwargs):
    self.fields = {}
    if ("big_endian" in kwargs):
      self.big_endian = kwargs["big_endian"]
      del kwargs["big_endian"]
    else:
      self.big_endian = True
    datablock.DataBlock.__init__(self, **kwargs)
    
  def getTagPayload(self, tag_num):
    """Returns the payload from a certain tag name or number."""
    
    # Get the tag number
    #tag_num = self.__getTagNum__(tag)

    if (tag_num in self.fields):
      tags = self.fields[tag_num]
    else:
      # If the tag was not found, return False
      return False

    # Decipher the relevant info
    data_type = self.records.query("num", tag_num, "data_type")
    payload = []
    for tag in tags:
      data = tag.getData()
      payload.append(DATA_TYPES[data_type].decode(data, self.big_endian))

    # Make sure that single values of each read tag are returned a single value
    # and not as list
    for index in range(len(payload)):
      if (len(payload[index]) == 1):
        payload[index] = payload[index][0]
        
    # If only a single tag was read, return only that value
    if (len(payload) == 1):
      payload = payload[0]
    
    return payload

  def removeTag(self, tag_num):
    """ Remove tag with the specified number. """
    
    self.fields[tag_num] = []

  def setTag(self, tag_num, payload):
    """Sets the payload for a certain tag num or tag name."""

    self.fields[tag_num] = [self.__getTagObj__(tag_num, payload)]

  def appendTag(self, tag_num, payload):
    """ Append a tag with specified tag number and payload. """
    
    if not (tag_num in self.fields):
      self.setTag(tag_num, payload)
    else:
      self.fields[tag_num].append(self.__getTagObj__(tag_num, payload))
      
  def getBlob(self):
    """ Return a binary string representing the IPTC record. """
    
    data_str = ""
    
    for tag_num in self.getTagNums():
      for tag in self.fields[tag_num]:
        data_str += "\x1C" + chr(self.RECORD_NUM) + chr(tag_num)
        data_length = tag.getDataLength()
        if (data_length > 32767):
          # We should encode an extended tag
          data_length = data_length & 32768 # 10000000 00000000
          data_str += byteform.itob(4, 2, big_endian = self.big_endian) # We cannoot encode it in two bytes, encode it in four. Formally this is incorrect, but in practice this will always do
          
        data_str += byteform.itob(data_length, 2, big_endian = self.big_endian)
        data_str += tag.getData()
        
    return data_str

  def __getTagObj__(self, tag_num, payload):
    """ Helper method to prepare a tag object for setTag and appendTag. """
    
    # Get the index and check if we can set this tag
    index = self.records.query("num", tag_num)
    if (index is False):
      raise KeyError, "Tag %d is not known in this IFD!" % tag_num
        
    # Find out the data type for the tag num and make sure it's a list
    data_type = self.records.query(index, "data_type")
    
    # Retrieve the allowed lengths
    count = self.records.query(index, "count")
    if (type(count) == types.ListType):
      min_count, max_count = count
    else:
      min_count = count
      max_count = count
      
    # Check if the payload has enough data
    if (type(payload) not in [types.ListType, types.TupleType, types.StringType]):
      paylaod = [payload]
    if ((len(payload) < min_count) or (len(payload) > max_count)):
      raise "Wrong number of arguments supplied to encode tag %s!" % str(tag_num)

    # Encode the data
    data = DATA_TYPES[data_type].encode(payload, self.big_endian)
    
    # If data type is Digits, pad it with zeroes
    if (data_type == 15):
      word_width = DATA_TYPES[data_type].word_width
      data = ((min_count * word_width) - len(data)) * "0" + data
      
    return datablock.DataBlock(data = data)    

