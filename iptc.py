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
      classes should have a QDB named tags with the following lists:
      - name : the names of the tags
      - num  : the numbers of the tags
      - count: the number of words every tag should occupy, with None
                    to indicate that this is free
      - type : the numbers of tag data types of the tags, as found in
                DATA_TYPES
      Furthermore, each record should have a variable called RECORD_NUM, which
      holds the record number as described in the IPTC/NAA spec.
  """
  
  # The data types we know of
  DATA_TYPES = DATA_TYPES
  
  def __init__(self, **kwargs):
    """ Initialize with a file pointer and offset and optionally length, or with
        data (like DataBlock). The big_endian boolean parameter specifies
        whether the data is in big endian format (defaults to True). """
    
    # Store the tags in the fields dict, where the keys are the tag numbers, and
    # the values are lists of DataBlocks (since IPTC tags may sometimes be
    # repeated.
    self.fields = {}
    
    # Prepare the data for the base class
    if ("big_endian" in kwargs):
      self.big_endian = kwargs["big_endian"]
      del kwargs["big_endian"]
    else:
      self.big_endian = True
    metainfofile.MetaInfoRecord.__init__(self, **kwargs)
    
  def getTag(self, tag_num, data_type = None):
    """Return the payload from a certain tag number."""
    
    if (tag_num in self.fields):
      tags = self.fields[tag_num]
    else:
      # If the tag was not found, return False
      return False

    # Get the data type
    if not (data_type):
      index = self.tags.query("num", tag_num)
      if (index == False):
        raise "Unknown tag and no data type provided, so I don't know how to decode it"
      data_type = self.tags.query(index, "data_type")

    # Decipher the relevant info
    payload = []
    for tag in tags:
      data = tag.getData()
      payload.append(self.DATA_TYPES[data_type].decode(data, self.big_endian))

    # Make sure that single values of each read tag are returned a single value
    # and not as list
    for index in range(len(payload)):
      if (len(payload[index]) == 1):
        payload[index] = payload[index][0]
        
    # If only a single tag was read, return only that value
    if (len(payload) == 1):
      payload = payload[0]
    
    return payload

  def setTag(self, tag_num, payload = None, check = True, data_type = None, count = None, data = None):
    """ Sets the payload for a certain tag num or tag name. If check is False,
        the method doesn't check if it knows of this tag. In this case however,
        a data type (integer) and optionaly data count or a binary encoded data
        string should be provided. """

    # Set a list with only this tag
    self.fields[tag_num] = [self.__getTagObj__(tag_num, payload, check, data_type, count, data)]

  def appendTag(self, tag_num, payload = None, check = True, data_type = None, count = None, data = None):
    """ Appends a tag with the specified payload. for a certain tag num or tag 
        name. If check is False, the method doesn't check if it knows of this
        tag. In this case however, a data type (integer) and optionaly data
        count or a binary encoded data string should be provided. """

    # If we don't have this tag in our internal list, append it with a list
    # containing one new tag object
    if not (tag_num in self.fields):
      self.setTag(tag_num, payload, check, data_type, count, data)
    # Otherwise, append the new tag object to the existing list
    else:
      self.fields[tag_num].append(self.__getTagObj__(tag_num, payload, check, data_type, count, data))

  def removeTag(self, tag_num):
    """ Remove tag with the specified number. """

    # Check if we know of this tag, and if this is the case, set it to an empty
    # list
    if self.tags.query("num", tag_num):
      self.fields[tag_num] = []

  def getBlob(self):
    """ Return a binary string representing the IPTC record. """
    
    data_str = ""
    
    # Iterate over all the tag numbers
    for tag_num in self.getTagNums():
      # Iterate over all the tags set with this number
      for tag in self.fields[tag_num]:
        # Each tag starts with 0x1C, the record number, and the tag number
        data_str += "\x1C" + chr(self.RECORD_NUM) + chr(tag_num)
        
        # If the number of data bytes exceeds 32767, we should encode an extended tag
        data_length = tag.getDataLength()
        if (data_length > 32767):
          # Extended tags are indicated with a 1 for the most significant bit
          data_length = data_length & 32768 # 10000000 00000000
          # An extended tag uses two bytes to specify the number of bytes to
          # encode the length of the data. If we cannot encode the length in
          # two bytes, we only know how to encode it in four bytes. In
          # practive this will always do.
          data_str += byteform.itob(4, 2, big_endian = self.big_endian)
          
        # Append the data length in bytes, and the actual binary data
        data_str += byteform.itob(data_length, 2, big_endian = self.big_endian)
        data_str += tag.getData()
        
    return data_str

  def __getTagObj__(self, tag_num, payload = None, check = True, data_type = None, count = None, data = None):
    """ Helper method to prepare a tag object for setTag and appendTag. """

    # Get the index and check if we can set this tag
    index = self.tags.query("num", tag_num)
    if (index is False):
      if (check):
        raise KeyError, "Tag %d is not known in this record!" % tag_num
      else:
        if not ((data_type) or (data)):
          raise KeyError, "Unknown tag %d, and no further way to encode it" % tag_num

    # If the user wants to set the data herself, check if its of the correct 
    # type
    if (data):
      if (type(data) != types.StringType):
        raise TypeError, "IPTC data should be a binary string"
    # Otherwise, encode it
    elif (payload):
      # Find out the data type for the tag num
      if (not data_type):
        data_type = self.tags.query(index, "data_type")
      
      # Retrieve the allowed lengths
      if (not count):
        count = self.tags.query(index, "count")
      if (type(count) == types.ListType):
        min_count, max_count = count
      else:
        min_count = count
        max_count = count
        
      # Check if the payload has enough data
      if (type(payload) not in [types.ListType, types.TupleType, types.StringType]):
        payload = [payload]
      if ((min_count) and (max_count)): # This might not be the case if we encode an unknown tag and the user didn't supply a count
        if ((len(payload) < min_count) or (len(payload) > max_count)):
          raise "Wrong number of arguments supplied to encode tag %s!" % str(tag_num)
  
      # Encode the data
      data = DATA_TYPES[data_type].encode(payload, self.big_endian)
      
      # If data type is Digits, pad it with zeroes
      if (data_type == 15):
        word_width = DATA_TYPES[data_type].word_width
        data = ((min_count * word_width) - len(data)) * "0" + data
    else:
      raise "Specify either a payload and optionally means to encode, or binary data"
      
    return datablock.DataBlock(data = data)
