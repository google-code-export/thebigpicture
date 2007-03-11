import types, byteform, ifddatatypes

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
    self.mapDiskFields()
    
    # The relevant fields (tags, whatever you want to call it) are stored in the
    # dict self.user_fields. The key is the field type (number), and the value
    # is a list of [data_type, encoded data]
    self.user_fields = {}

  def mapDiskFields(self):
    self.disk_fields = {} # The map
    
    # Go to the proper offset and read the first two bytes. They represent the
    # number of fields in the IFD
    self.fp.seek(self.ifd_offset)
    num_fields = byteform.btoi(self.fp.read(2), big_endian = self.is_be)

    for field_num in range(num_fields):
      # Read the type of the tag (number), the way the payload is stored, and
      # the length of the payload
      tag_type    = byteform.btoi(self.fp.read(2), big_endian = self.is_be)
      data_type   = byteform.btoi(self.fp.read(2), big_endian = self.is_be)
      payload_len = byteform.btoi(self.fp.read(4), big_endian = self.is_be)

      # The word width (number of bytes to encode one "character") of the
      # payload is determined by the data type. This needs to be multiplied by
      # the number of characters to get the total number of bytes.
      num_bytes = payload_len * ifddatatypes.TYPES[data_type].word_width
        
      # The next four bytes either encode an offset te where the payload can be
      # found, or the payload itself if it fits in these four bytes.
      if (num_bytes < 5):
        payload_offset = self.fp.tell() - self.header_offset
        self.fp.read(4)
      else:
        payload_offset = byteform.btoi(self.fp.read(4), big_endian = self.is_be)
        
      self.disk_fields[tag_type] = [payload_offset, data_type, num_bytes]

  def getTagPayload(self, tag):
    """Returns the payload from a certain tag name or number."""
    
    # Get the tag number
    tag_num = self.__getTagNum(tag)

    if (tag_num) and (tag_num in self.user_fields):
      # If the tag is specifically set, return its value
      data_type, data = self.user_fields[tag_num]
    elif (tag_num) and (tag_num in self.disk_fields):
      # Seek to the correct location and read the data
      offset, data_type, length = self.disk_fields[tag_num]
      self.fp.seek(offset + self.header_offset)
      data = self.fp.read(length)
    else:
      # If the tag was not found, return False
      return False
      
    payload = ifddatatypes.TYPES[data_type].decode(data, self.is_be)

    # If the data is a single value, return it as such, otherwise, return a
    # list
    if (len(payload) == 1):
      return payload[0]
    else:
      return payload
    
  def setTagPayload(self, tag, payload):
    """Sets the payload for a certain tag num or tag name."""
    
    # Get the tag num for the tag
    tag_num = self.__getTagNum(tag)
    
    if (tag_num):
      index = self.tag_nums.index(tag_num)

      # Make sure the payload is a sequence      
      if (type(payload) not in [types.ListType, types.TupleType]):
        payload = [payload]
        
      # Check if the supplied data is of correct length
      req_count = self.data_counts[index]
      if (req_count != None) and (req_count != -1):
        if (len(payload) != req_count):
          raise "Wrong number of arguments supplied for encoding this tag!"
      
      # Find out the data type for the tag num and make sure it's a list
      data_types = self.data_types[index]
      if (type(data_types) == types.IntType):
        data_types = [data_types]
      
      # Try to encode the data with each of the possible data types. Stop when
      # we succeeded.
      success = False
      for data_type in data_types:
        try:
          data = ifddatatypes.TYPES[data_type].encode(payload, self.is_be)
          success = True
        except:
          pass
        if (success):
          break
        
      # Set the used data type and payload
      self.user_fields[tag_num] = [data_type, data]

  def getTagNums(self):
    """ Return a sorted list of set tag nums in this IFD. """
    
    # Get all the unique tags using a set
    tag_nums = set(self.disk_fields) | set(self.user_fields)
    
    # Sort them
    tag_nums = list(tag_nums)
    tag_nums.sort()
    
    return tag_nums
    
  def getSize(self):
    """ Calculate the byte size of the IFD. """
    
    tag_nums = self.getTagNums()
    
    # An IFD always needs 2 bytes at the start to specify the number of fields,
    # and 4 bytes between the fields and the data for the byte offset to the
    # next IFD
    size = 6
    
    # For each field, we need 12 bytes
    size += 12 * len(tag_nums)

    # For each field with a data block larger than four bytes, we need to add
    # the size of the data field
    for tag_num in tag_nums:
      if (tag_num in self.user_fields):
        num_bytes = len(self.user_fields[tag_num][1])
      else:
        num_bytes = self.disk_fields[tag_num][2]
      
      if (num_bytes > 4):
        size += num_bytes
    return size
    
  def getByteStream(self, offset, next_ifd = 0):
    """Returns the entry stream and the data stream for writing the IFD. offset
    is the offset to byte addresses specified in tghe IFD (usually the size of
    the TIFF header). next_ifd is the byte position for the next IFD, if any.
    """
    
    tag_nums = self.getTagNums()

    # Calculate the offset at which we may write data (after the offset, 2 bytes
    # at the start of the IFD, 12 bytes for each field, and four bytes as
    # pointer to the next IFD.
    data_offset = offset + 12 * len(tag_nums) + 6
   
    # For writing the data, we split the stream in two; one part contains the
    # 12-byte fields specifying tags, data type, etc. and the other one contains
    # the encoded data (which is over 4 bytes in size). At the end, these two
    # fields will be concatenated
    fields_stream = byteform.itob(len(tag_nums), 2, big_endian = self.is_be)
    data_stream   = byteform.itob(next_ifd, 4, big_endian = self.is_be)
    
    # Write each tag
    for tag_num in tag_nums:
      if (tag_num in self.user_fields):
        data_type, data = self.user_fields[tag_num]
      else:
        data_type = self.disk_fields[tag_num][1]
        self.fp.seek(self.disk_fields[tag_num][0])
        data = self.fp.read(self.disk_fields[tag_num][2])
        
      count = len(data) / ifddatatypes.TYPES[data_type].word_width
        
      # Construct the field
      fields_stream += byteform.itob(tag_num, 2, big_endian = self.is_be)
      fields_stream += byteform.itob(data_type, 2, big_endian = self.is_be)
      fields_stream += byteform.itob(count, 4, big_endian = self.is_be)
      if (len(data) <= 4):
        fields_stream += data
        fields_stream += (4 - len(data)) * "\x00"
      else:
        fields_stream += byteform.itob(data_offset, 4, big_endian = self.is_be)
        data_stream   += data
        data_offset   += len(data)
        
    return fields_stream + data_stream
    
  def __getTagNum(self, tag):
    """ Find out if a tag name or number is known, and return its number or
        False otherwise. """
    
    ret = False
    
    if (type(tag) == types.IntType):
      # We have a tag number as user input
      if tag in self.tag_nums:
        ret = tag
    elif (type(tag) == types.StringType):
      # We have a tag name, search the number for it
      try:
        index = self.tag_names.index(tag)
        ret = self.tag_nums[index]
      except ValueError:
        pass
  
    return ret
    
#  def getDiskSize(self):
#    """Return the size in bytes of the IDF on disk, including the 2 bytes that
#    specify the number of fields."""
#    return 2 + (len(self.disk_fields) * 12)
 
