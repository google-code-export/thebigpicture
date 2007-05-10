class DataBlock:
  """ General class for a data block on disk or in memory, which may be an Exif,
      IPTC, Photoshop, (...) element, but also a tag in one of these elements.
      It can either save a file pointer, offset and optional length, or actual
      binary data. """
      
  def __init__(self, fp = None, offset = 0, length = 0, data = None):
    """ A tag may be initialized with binary data or with a file pointer. Both
        forms may provide an offset of where the data actually starts, and a 
        data length. """

    # Do some calling checks
    proper_call = True
    if (fp) and (data):
      raise TypeError, "Either initialize a DataBlock with file pointer or with a binary data!"
      
    if (not offset):
      offset = 0 # It's possible that we're called with None as offset
      
    self.data_offset = offset
    self.length      = length
    self.fp          = None
    self.data        = None

    # Check in which form we were called
    if (fp):
      self.fp = fp
    elif (data):
      self.setData(data, offset)
    else:
      self.length = 0
    
    # Keep track of the current position when reading from file or string
    self.byte_pos = self.data_offset

  def setData(self, data, offset):
    """ Set the data of the tag to the specified binary string, along with a new
        offset. """

    self.data        = buffer(data)
    self.fp          = None
    self.data_offset = offset
    self.seek(0)
    
  def getDataLength(self):
    """ Return the length of the data, or None if this is unknown. """
    
    if (self.length):
      return self.length
    elif (self.data):
      return len(self.data) - self.data_offset
    else:
      return None
      
  def read(self, num_bytes = None, seek = None):
    """ Read the specified number of bytes from the content, or to the end of
        the data if num_bytes is None. The optional seek arguments tells the
        method first to seek to this position. """
    
    data = None
    
    # Seek to the specified position, or otherwise make sure we're in the right
    # position
    if (seek == None): # Explicit test, because 0 is a valid value 
      seek = self.tell()
    self.seek(seek)

    # Read the bytes from file
    if (self.fp):
      if (num_bytes == None):
        if (self.getDataLength()):
          num_bytes = self.getDataLength() - self.tell()
        else:
          num_bytes = -1
      data = self.fp.read(num_bytes)
      
    # Read the bytes from buffer
    elif (self.data):
      if (num_bytes == None) or ((num_bytes) and ((num_bytes - self.tell()) > self.getDataLength())):
        num_bytes = self.getDataLength() - self.tell()

      data = self.data[self.byte_pos:self.byte_pos + num_bytes]
      
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
      self.byte_pos = position + self.data_offset
      if (self.fp):
        self.fp.seek(self.byte_pos)

  def getData(self):
    """ Return the data blob. """
    return self.read(seek = 0)
    
  def getDataOffset(self):
    """ Return the offset in the file where the data can be found, or None
        if the data is user set. """
        
    return self.data_offset
    
  def tell(self):
    """ Return the current offset in the file or data stream, measured from the
        data offset. """
    
    return self.byte_pos - self.data_offset
