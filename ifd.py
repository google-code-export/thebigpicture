from helper import convBytes2Int, convInt2Bytes, convBytes2Float

import types, byteform

class IFD:
  """An IFD (Image File Directory) represents an elementary data type in both a
  Tiff and an Exif file. It has a certain ifd_offset in the file. A
  header_offset may also be specified to determine the start of the enclosing,
  larger part (APP0 for example). Offsets in an IFD are measured from this
  number. This class functions as a base class. Derived classes need to specify
  the arrays tag_names, tag_nums and required_tags. The first is an array with
  the string representation of the names of the tags, the second one holds the
  numerical values in the same order. The third array holds the number of all
  the required tags. """
  
  def __init__(self, file_pointer, ifd_offset, header_offset = 0, is_be = True):
    self.fp            = file_pointer
    self.header_offset = header_offset
    self.ifd_offset    = ifd_offset + self.header_offset
    self.is_be         = is_be
        
    # This dict stores the relevant locations for each field in the IDF. The
    # key is the field type (number), and the data is a list of 
    # [offset, data type, number of bytes]
    self.disk_fields = {}
    self.mapFields()
    
    # The relevant fields (tags, whatever you want to call it) are stored in the
    # dict self.user_fields. The key is the field type (number), and the value
    # can be either be the data or False, which means that the data is not user
    # set but can be retreived from disk.
    self.user_fields = {}

  def mapFields(self):
    self.disk_fields = {} # The map
    
    # Go to the proper offset and read the first two bytes. They represent the
    # number of fields in the IFD
    self.fp.seek(self.ifd_offset)
    num_fields = convBytes2Int(self.fp.read(2), self.is_be)

    for field_num in range(num_fields):
      # Read the type of the tag (number), the way the payload is stored, and
      # the length of the payload
      tag_type    = byteform.btoi(self.fp.read(2), big_endian = self.is_be)
      data_type   = byteform.btoi(self.fp.read(2), big_endian = self.is_be)
      payload_len = byteform.btoi(self.fp.read(4), big_endian = self.is_be)

      # The char-width (number of bytes to encode one "character") of the
      # payload is determined by the data type. This needs to be multiplied by
      # the number of characters to get the total number of bytes.
      if (data_type in [1, 2, 6, 7]): # BYTE, ASCII, SBYTE, UNDEFINED 8-bit
        num_bytes = payload_len
      elif (data_type in [3, 8]): # SHORT, SSHORT
        num_bytes = payload_len * 2
      elif (data_type in [4, 9, 11]): # LONG, SLONG. FLOAT
        num_bytes = payload_len * 4
      elif (data_type in [5, 10, 12]): # RATIONAL, SRATIONAL, DOUBLE
        num_bytes = payload_len * 8
        
      # The next four bytes either encode an offset te where the payload can be
      # found, or the payload itself if it fits in these four bytes.
      if (num_bytes < 5):
        payload_offset = self.fp.tell() - self.header_offset
        self.fp.read(4)
      else:
        payload_offset = convBytes2Int(self.fp.read(4), self.is_be)
        
      self.disk_fields[tag_type] = [payload_offset, data_type, num_bytes]

  def getPayload(self, tag):
    """Returns the payload from a certain tag name or number."""
    
    # Check to see if we have a name or number
    if (type(tag) == types.IntType):
      tag_num = tag
    elif (type(tag) == types.StringType):
      tag_num = self.__getTagNumFromName(tag)

    if (tag_num) and (tag_num in self.user_fields):
      # If the tag is specifically set, return its value
      return self.user_fields[tag_num]
    elif (tag_num) and (tag_num in self.disk_fields):
      # Seek to the correct location and read the raw data
      offset, data_type, length = self.disk_fields[tag_num]
      self.fp.seek(offset + self.header_offset)
      data = self.fp.read(length)
      
      # Decode the data
      if (data_type == 2): # ASCII
        ret = data[:-1]
      else:
        ret = []
        
        # Figure out the bytes per character
        if (data_type in [1, 6, 7]): # BYTE, SBYTE, UNDEFINED 
          char_width = 1
        elif (data_type in [3, 8]): # SHORT, SSHORT
          char_width = 2
        elif (data_type in [4, 9, 11]): # LONG, SLONG, FLOAT
          char_width = 4
        elif (data_type in [5, 10, 12]): # RATIONAL, SRATIONAL, DOUBLE
          char_width = 8
        
        # Figure out whether it is signed
        if (data_type in [6, 8, 9, 10]):
          signed = True
        else:
          signed = False
        
        # Iterate over the data
        for char_num in range(0, len(data), char_width):
          if (data_type in [1, 3, 4, 6, 8, 9]): # BYTE, SHORT, LONG, SBYTE, SSHORT, SLONG
            app = convBytes2Int(data[char_num:char_num + char_width], self.is_be, signed)
          elif (data_type in [5, 10]): # RATIONAL, SRATIONAL
            frac  = convBytes2Int(data[char_num:char_num + 4], self.is_be, signed)
            denom = convBytes2Int(data[char_num + 4:char_num + 8], self.is_be, signed)
            app = [frac, denom]
          elif (data_type == 7): # UNDEFINED
            app = data[char_num]
          elif (data_type in [11, 12]): # FLOAT, DOUBLE
            app = convBytes2Float(data[char_num:char_num + char_width], self.is_be)
            
          ret.append(app)
      if (len(ret) == 1):
        return ret[0]
      else:
        return ret
    else:
      return False
      
  def getTypeByName(self, tag_name):
    tag_num = self.__getTagNumFromName(tag_name)
    if (tag_num):
      return self.__getType(tag_num)
    else:
      return False
      
  def getTypeByNum(self, tag_num):
    return self.__getType(tag_num)
  
  def __getType(self, tag_num):
    if (tag_num in self.user_fields):
      if (self.user_fields[tag_num] != False):
        # If the tag is specifically set, return its value
        pass
      else:
        return self.disk_fields[tag_num][1]
    else:
      return False
    
  def setPayload(self, tag_num, payload):
    """Sets the payload for a certain tag num or tag name."""
#    self.user_fields[tag_num] = payload
    index = tag_nums.index(tag_num)
    
    data_type = self.data_types[index]
#    if (type(data_types) != types.ListType):
#      data_types = [data_types]
      
#    for data_type in data_types:
    if (data_type in [6, 8, 9, 10]):
      signed = True
    else:
      signed = False

    # Uh-oh...word width != byte count
    if (data_type in [1, 3, 6, 7, 8]):
      if (data_type in [1, 6, 7]): # BYTE, SBYTE, UNDEFINED 
        char_width = 1
      elif (data_type in [3, 8]): # SHORT, SSHORT
        char_width = 2
      try:
        data = convInt2Bytes(self.user_fields[tag_num], char_width, self.is_be)
      except:
        pass
    elif (data_type in [4, 5, 9, 10, 11, 12]):
      if (data_type in [4, 9, 11]): # LONG, SLONG, FLOAT
        char_width = 4
      elif (data_type in [5, 10, 12]): # RATIONAL, SRATIONAL, DOUBLE
        char_width = 8
      try:
        data = convInt2Float(self.user_fields[tag_num], char_width, self.is_be)
      except:
        pass
    else:
      # Warning! Data should already be proper formatted
      data = self.user_fields[tag_num]

  def __getTagNumFromName(self, tag_name):
    """Gets the tag number associated with a certain tag name."""
    try:
      index = self.tag_names.index(tag_name)
    except ValueError:
      return False

    return self.tag_nums[index]
    
  def getReadSize(self):
    """Return the size in bytes of the IDF on disk, including the 2 bytes that
    specify the number of fields."""
    return 2 + (len(self.disk_fields) * 12)
  
  def getByteStream(self, data_offset):
    """Returns the entry stream and the data stream for writing the IFD. The
    data_offset determines at the extra amount of space the data offset needs
    (pointers between field and data stream, header offset, etc.) """
    
    # Get the tags we need to write (we don't need to sort them, a set is
    # already sorted
    tag_nums = set(self.disk_fields) | set(self.user_fields)

    # Calculate the total size off all the records
    data_offset += 12 * len(tag_nums) + 2 
   
    # For writing the data, we split the stream in two; one part contains the
    # 12-byte fields specifying tags, data type, etc. and the other one contains
    # the encoded data (which is over 4 bytes in size). At the end, these two
    # fields will be concatenated
    entry_stream = convInt2Bytes(len(tag_nums), 2, self.is_be)
    data_stream  = ""
    
    # Write each tag
    for tag_num in tag_nums:
      # Choose a data type to store the info in. If the data comes from an
      # image, just use the same data and type, otherwise, choose one based on
      # the Exif spec.
      if (tag_num in self.user_fields):
            
        data_length = len(data) 
        
      elif (tag_num in self.disk_fields):
        data_type, data_length = self.disk_fields[tag_num][1:]
        self.fp.seek(self.disk_fields[tag_num][0])
        data = self.fp.read(data_length)

      # Construct the field
      entry_stream += convInt2Bytes(tag_num, 2, self.is_be)
      entry_stream += convInt2Bytes(data_type, 2, self.is_be)
      entry_stream += convInt2Bytes(data_length, 4, self.is_be)
      if (data_length <= 4):
        entry_stream += data
        entry_stream += (4 - len(data)) * "\x00"
      else:
        entry_stream += convInt2Bytes(data_offset, 4, self.is_be)
        data_stream += data
        data_offset += data_length
        
    return entry_stream, data_stream
