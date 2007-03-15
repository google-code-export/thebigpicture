class Tag:
  """ General class for a tag, which may be an Exif, IPTC, Photoshop (...) tag.
      It can either save a file pointer, offset and length, or actual binary
      data. """
      
  def __init__(self, *args, **kwargs):
    """ A tag may be initialized with binary data, or a list of file pointer,
        offset and length in bytes, or a list of only file pointer and offset,
        but then the derived class should set the length parameter. """

    # Check in which form we were called
    if (len(args) == 0):
      self.fp          = None
      self.data_offset = None
      self.length      = None
      self.data        = None
    if (len(args) == 3):
      self.fp, self.data_offset, self.length = args
      self.data = None
    elif (len(args) == 1):
      self.fp          = None
      self.data_offset = None
      self.length      = None
      self.data        = args[0]
    else:
      raise "Initialize either with a file pointer, offset and length, or with a binary data string."
      
    # Check if the user set a big_endian keyword argument
    if ("big_endian" in kwargs):
      self.is_be = kwargs["big_endian"]
    else:
      self.is_be = True
  
    # Needed for reading from file or string
    self.byte_pos = 0

  def setData(self, data):
    """ Set the data of the tag to the specified binary string. """
    
    self.data        = data
    self.fp          = None
    self.data_offset = None
    self.length      = None
    
  def getDataLength(self):
    """ Return the length of the data. """
    
    if (self.data):
      return len(self.data)
    else:
      return self.length
      
  def read(self, num_bytes = None, seek = None):
    """ Read the specified number of bytes from the content, or to the end of
        the data if num_bytes is None. The optional seek arguments tells the
        method first to seek to this position. """
    
    data = None

    # Seek to the specified position
    if (seek):
      self.seek(seek)
      
    # Find out the number of bytes we should read
    if not (num_bytes):
      num_bytes = self.getDataLength() - self.byte_pos
      
    # Check if we can do the reading
    if ((self.byte_pos + num_bytes) > self.getDataLength()):
      raise "Attempt to read beyond the size of the data block!"
      
    # Read the bytes from either file or string
    if (self.fp) and (self.data_offset):
      self.fp.seek(self.data_offset + self.byte_pos)
      data = self.fp.read(num_bytes)
    elif (self.data):
      data = self.data[self.byte_pos:self.byte_pos + num_bytes]
      
    # Update the byte position
    self.byte_pos += num_bytes
    
    return data
    
  def seek(self, position):
    """ Sets the byte position to the specified position. """
    if (position > self.getDataLength()):
      raise "Trying to seek outside data block."
    else:
      self.byte_pos = position
    
  def getData(self):
    """ Return the data blob. """
    self.seek(0)
    return self.read()
    
  def getDataOffset(self):
    """ Return the offset in the file where the data can be found, or None
        if the data is useer set. """
        
    return self.data_offset
