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
import byteform, datablock, datatypes, metainfofile

# === Stuff relating to the IFD data types ===
class Ascii(datatypes.DataType):
  """ In exif, strings are capped with a zero byte, and a byte stream may
      contain multiple strings. """
  word_width = 1
  
  @classmethod
  def encode(cls, streams, is_big_endian = True):
    """ Encode either a string or a list of strings to ASCII data. The
    is_big_endian parameter is only here for compatibility reasons. """
    
    # If the user passed a string, put it in a list for easier handling
    if (type(streams) == types.StringType):
      streams = [streams]
      
    # Iterate over the strings and put a null character at each end
    byte_stream = ""
    for stream in streams:
      byte_stream += stream + "\x00"
      
    return byte_stream
    
  @classmethod
  def decode(cls, byte_stream, is_big_endian = True):
    """ Convert a byte stream to a list of strings. The is_big_endian parameter
        is only here for compatibility reasons. """
        
    streams = []
    curr_stream = ""
    
    # Iterate over all the characters in the byte stream, and start a new string
    # at every null character
    for char in byte_stream:
      if (char == "\x00"):
        if (len(curr_stream) > 0):
          streams.append(curr_stream)
        curr_stream = ""
      else:
        curr_stream += char

    return streams
    
DATA_TYPES = {
  1: datatypes.Byte,
  2: Ascii,
  3: datatypes.Short,
  4: datatypes.Long,
  5: datatypes.Rational,
  6: datatypes.SByte,
  7: datatypes.Undefined,
  8: datatypes.SShort,
  9: datatypes.SLong,
  10: datatypes.SRational,
  11: datatypes.Float,
  12: datatypes.Double
} 

# === Stuff relating to the IFD structure ===
class Tag(datablock.DataBlock):
  """ An IFD tag. It is basically a DataBlock with a data type associated, since
      IFD tags may sometimes be encoded with differing data types. """
  
  def __init__(self, *args):
    """ Initialize either with file pointer, offset, length, and data type, or
        the encoded content and data type. """
      
    # Construct a dict for the base class
    base_kwargs = {}
    
    # Check if we were called with data or with file pointer
    if (len(args) == 2):
      base_kwargs["data"] = args[0]
    elif (len(args) == 4):
      base_kwargs["fp"]     = args[0]
      base_kwargs["offset"] = args[1]
      base_kwargs["length"] = args[2]
    else:
      raise TypeError, "Wrong initialization of Exif tag!"
      
    # The data type is always the last argument
    self.data_type = args[-1]
      
    # Initialize the base class. The endianness does not even matter, it is
    # never used.
    datablock.DataBlock.__init__(self, **base_kwargs)
    
  def getDataType(self):
    """ Return the data type of the tag. """
    return self.data_type
      
class IFD(metainfofile.MetaInfoRecord):
  """An IFD (Image File Directory) represents an elementary data type in both a
  Tiff and an Exif file. It has a certain ifd_offset in the file. A
  header_offset may also be specified to determine the start of the enclosing,
  larger part (APP1 for example). Offsets in an IFD are measured from this
  number. This class functions as a base class.
  Derived classes need to specify a QDB called tags, which holds the names,
  numbers, data types and counts for each tag.
  After loading, the class has a variable called next_ifd_offset, which 
  specifies the read offset to the next IFD. """

  # The data types we know of
  DATA_TYPES = DATA_TYPES
  
  def __init__(self, file_pointer = None, ifd_offset = None, header_offset = 0, data = None, big_endian = True):
    
    # Construct the arguments for the base class
    base_kwargs = {}
    if ((file_pointer) and (ifd_offset)):
      base_kwargs["fp"]     = file_pointer
      base_kwargs["offset"] = ifd_offset + header_offset
    elif (data):
      base_kwargs["data"] = data
      
    # Call the base class
    metainfofile.MetaInfoRecord.__init__(self, **base_kwargs)
    
    # Store the data relevant to this class
    self.ifd_offset    = ifd_offset
    self.header_offset = header_offset
    self.big_endian    = big_endian
    
    self.next_ifd_offset = 0

    # The fields dict stores all the tags read from disk and/or set by the user.
    self.mapDiskFields()
    
  def mapDiskFields(self):
    """ Reads the exif structure from disk and maps all the fields. """
    self.fields = {} # Empty the map
    
    # Go to the proper offset and read the first two bytes. They represent the
    # number of fields in the IFD
    if (self.getDataLength() > 0) or (self.getDataLength() == None): # Parse when there's data, or when data size is unknown
      self.seek(0)
      num_fields = byteform.btousi(self.read(2), big_endian = self.big_endian)
  
      for field_num in range(num_fields):
        # Read the type of the tag (number), the way the payload is stored, and
        # the length of the payload
        tag_type    = byteform.btousi(self.read(2), big_endian = self.big_endian)
        data_type   = byteform.btousi(self.read(2), big_endian = self.big_endian)
        payload_len = byteform.btousi(self.read(4), big_endian = self.big_endian)
  
        # The word width (number of bytes to encode one "character") of the
        # payload is determined by the data type. This needs to be multiplied by
        # the number of characters to get the total number of bytes.
        num_bytes = payload_len * DATA_TYPES[data_type].word_width
          
        # The next four bytes either encode an offset te where the payload can be
        # found, or the payload itself if it fits in these four bytes.
        if (num_bytes < 5):
          payload_offset = self.tell() + self.header_offset
          self.read(4)
        else:
          payload_offset = byteform.btousi(self.read(4), big_endian = self.big_endian) + self.header_offset - self.ifd_offset

        # Store the tag. This method does not check if we know the tag type, and
        # that's exactly what we want.
        if (self.fp):
          tag = Tag(self.fp, payload_offset + self.ifd_offset, num_bytes, data_type)
        else:
          tag = Tag(self.read(num_bytes, payload_offset + self.header_offset), data_type)
        self.fields[tag_type] = tag
      self.next_ifd_offset = byteform.btoi(self.read(4), big_endian = self.big_endian)

  def getTag(self, tag_num):
    """Returns the payload from a certain tag number. """
    
    if (tag_num in self.fields):
      tag = self.fields[tag_num]
    else:
      # If the tag was not found, return False
      return False

    # Decipher the relevant info
    data_type = tag.getDataType()
    data      = tag.getData()
    payload   = self.DATA_TYPES[data_type].decode(data, self.big_endian)

    # If the tag is empty, return None. Else if data is a single value, return 
    # it as such, otherwise, return a list
    if (len(payload) == 0):
      return None
    elif (len(payload) == 1):
      return payload[0]
    else:
      return payload

  def setTag(self, tag_num, payload = None, check = True, data_type = None, count = None, data = None):
    """ Sets the (unencoded) payload or (binary encoded) data for a certain tag 
        num or tag name. If check is False, the method doesn't check if it knows
        of this tag. In this case however, a data type (integer) needs to be
        provided. In the case of payload, the optional count parameter can
        provide a sanuty check. """

    # Get the index and check if we can set this tag
    index = self.tags.query("num", tag_num)
    if (index is False):
      if (check):
        raise KeyError, "Tag %d is not known in this IFD!" % tag_num
      else:
        if not ((data_type) or (data)):
          raise KeyError, "Unknown tag %d, and no further way to encode it" % tag_num

    # If the user supplied data, use that
    if (data):
      # Check for the correct parameters
      if (type(data) != types.StringType):
        raise TypeError, "IFD data should be a binary string"
      if (type(data_types) != types.IntType):
        raise TypeError, "When setting an IFD tag directly with binary data, you need to specify exactly one data type"
    # Otherwise, encode the tag ourselve
    else:
      # Make sure the payload is in a sequence or string 
      if (type(payload) not in [types.ListType, types.TupleType, types.StringType]):
        payload = [payload]
        
      # Check if the supplied data is of correct length
      if (not count) and (index):
        count = self.tags.query("num", tag_num, "count")
      if (count != None) and (count != False) and (count != -1): # Unknonw, unspecified or special
        if (len(payload) != count):
          raise "Wrong number of arguments supplied for encoding this tag!"
      
      # Find out the data type for the tag num and make sure it's a list
      if (data_type):
        data_types = data_type
        del(data_type)
      else:
        data_types = self.tags.query("num", tag_num, "data_type")
      if (type(data_types) == types.IntType):
        data_types = [data_types]
      
      # Try to encode the data with each of the possible data types. Stop when
      # we succeeded.
      success = False
      for data_type in data_types:
        try:
          data = DATA_TYPES[data_type].encode(payload, self.big_endian)
          success = True
        except:
          pass
        if (success):
          break
          
      if (data == None):
        raise "Error encoding data for tag %d!" % tag_num

    # Set the used data type and payload
    self.fields[tag_num] = Tag(data, data_type)

  def removeTag(self, tag_num):
    """ Remove tag with the specified number. """
    try:
      del(self.fields[tag_num])
    except KeyError:
      pass
    
  def getSize(self, next_ifd = True):
    """ Calculate the byte size of the
    IFD. """
    
    if not (self.hasTags()):
      # If we don't have any tags, length is zero
      return 0
    else:
      tag_nums = self.fields.keys()
      
      # An IFD always needs 2 bytes at the start to specify the number of fields
      size = 2
      
      # If we should write a next IFD pointer, we need four bytes
      size += 4
      
      # For each field, we need 12 bytes
      size += 12 * len(tag_nums)
  
      # For each field with a data block larger than four bytes, we need to add
      # the size of the data field
      for tag_num in tag_nums:
        tag       = self.fields[tag_num]
        num_bytes = tag.getDataLength()
        if (num_bytes > 4):
          size += num_bytes
          
      return size
    
  def getBlob(self, offset, next_ifd = 0):
    """Returns the entry stream and the data stream for writing the IFD. offset
    is the offset to byte addresses specified in tghe IFD (usually the size of
    the TIFF header). next_ifd is the byte position for the next IFD, if any.
    If next_ifd is set to None, it will be omitted
    """
    
    if not (self.hasTags()):
      # If we don't have any tags, simply return nothing
      return None
    else:
      tag_nums = self.getTagNums()
  
      # For writing the data, we split the stream in two; one part contains the
      # 12-byte fields specifying tags, data type, etc. and the other one contains
      # the encoded data (which is over 4 bytes in size). At the end, these two
      # fields will be concatenated
      fields_stream = byteform.itob(len(tag_nums), 2, big_endian = self.big_endian)
      data_stream = ""
      
      # Calculate the offset at which we may write data (after the offset, 2
      # bytes at the start of the IFD and 12 bytes for each field
      data_offset = offset + 12 * len(tag_nums) + 2

      # If we have a pointer to the next IFD, write it to the data stream
      if (next_ifd != None):
        data_stream = byteform.itob(next_ifd, 4, big_endian = self.big_endian)
        data_offset += 4

      # Write each tag
      for tag_num in tag_nums:
        tag       = self.fields[tag_num]
        data_type = tag.getDataType()
        data      = tag.getData()
        count     = len(data) / DATA_TYPES[data_type].word_width
        
        # Write the tag number, data type and data count
        fields_stream += byteform.itob(tag_num, 2, big_endian = self.big_endian)
        fields_stream += byteform.itob(data_type, 2, big_endian = self.big_endian)
        fields_stream += byteform.itob(count, 4, big_endian = self.big_endian)
        
        # If we can fit the data into four bytes, do so, otherwise write it in
        # the data field and store the offset
        if (len(data) <= 4):
          fields_stream += data
          fields_stream += (4 - len(data)) * "\x00"
        else:
          fields_stream += byteform.itob(data_offset, 4, big_endian = self.big_endian)
          data_stream   += data
          data_offset   += len(data)
          
      return fields_stream + data_stream
