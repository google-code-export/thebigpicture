class DataBlock:
  """ General class for a data block on disk or in memory, which may be an Exif,
      IPTC, Photoshop (...) element, but also a tag in one of these elements.
      It can either save a file pointer, offset and optional length, or actual
      binary data. """
      
  def __init__(self, fp = None, offset = None, length = None, data = None):
    """ A tag may be initialized with binary data, or a list of file pointer,
        offset and optionally a length in bytes. """

    # Do some calling checks
    proper_call = True
    if (fp or offset or length):
      if (data):
        proper_call = False
      if not (fp and offset):
        proper_call = False
    if not (proper_call):
      raise TypeError, "Either initialize a Tag with file pointer, byte offset and optional length, or with a data block!"
      
    # Check in which form we were called
    self.fp          = None
    self.data_offset = None
    self.length      = None
    self.data        = None
    
    if (fp):
      self.fp          = fp
      self.data_offset = offset
      self.length      = length
    elif (data):
      self.setData(data)
    else:
      self.length = 0
    
    # Needed for reading from file or string
    self.byte_pos = 0

  def setData(self, data):
    """ Set the data of the tag to the specified binary string. """

    self.data        = data
    self.fp          = None
    self.data_offset = None
    self.length      = None
    
  def getDataLength(self):
    """ Return the length of the data, or None if this is unknown. """
    
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
    if (seek != None): # Explicit test, because 0 is a valid value 
      self.seek(seek)

    if (num_bytes != None):
      # Check if we can do the reading
      length = self.getDataLength()
      if (length) and ((self.byte_pos + num_bytes) > length):
        raise IOError, "Attempt to read beyond the size of the data block!"

    # Read the bytes from either file or string
    if (self.fp) and (self.data_offset):
      self.fp.seek(self.data_offset + self.byte_pos)
      if (num_bytes == None):
        if (self.length):
          num_bytes = self.length - self.byte_pos
        else:
          num_bytes = -1
      data = self.fp.read(num_bytes)
    elif (self.data):
      if (num_bytes != None):
        data = self.data[self.byte_pos:self.byte_pos + num_bytes]
      else:
        data = self.data[self.byte_pos:]
      
    # Update the byte position
    if (data):
      self.byte_pos += len(data)
    
    return data
    
  def seek(self, position):
    """ Sets the byte position to the specified position. """

    data_length = self.getDataLength()
    if (data_length) and (position > data_length):
      raise IOError, "Trying to seek outside data block."
    else:
      self.byte_pos = position

  def getData(self):
    """ Return the data blob. """
    return self.read(seek = 0)
    
  def getDataOffset(self):
    """ Return the offset in the file where the data can be found, or None
        if the data is user set. """
        
    return self.data_offset
    
  def tell(self):
    """ Return the current offset in the file or data stream. """
    
    return self.byte_pos
