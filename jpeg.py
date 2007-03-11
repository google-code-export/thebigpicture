import exif, tiff, metainfofile, iptc
from helper import convBytes2Int

import types

# JPEG files are divided in several segments, each starting with \xff, followed
# by a byte soecifying the segment, foloowed by two bytes specifying the length
# of the segment.
# Exif data and XMP data both reside in an APP1 segment (of which multiple may
# exist). An Exif APP1 segment is identified by "Exif" following the two bytes
# specifying the length of the segment. An XMP APP1 segment is specified by
# "http://ns.adobe.com/xap/1.0"
# JPEG Comments have their own segment, identified by \xfe (COM). The entire
# segment is occupied by the comment.

class JPEG(metainfofile.MetaInfoFile):
  """Parse and write JPEG files."""

  # JPEG files are always big endian
  is_be = True
  
  def __init__(self, file_indicator, offset = 0):
    """Initialize a JPEG file object. It needs an open file object or a path to
    a file on the disk. A byte offset may be given to the start of the JPEG
    header."""
    
    metainfofile.MetaInfoFile.__init__(self)
    
    # Initialize the file pointer
    if (type(file_indicator) == types.StringType):
      self.fp = file(file_indicator)
    elif (type(file_indicator) == types.FileType):
      self.fp = file_indicator
    else:
      raise "No valid file parameter given -- file path or file object needed." 
    
    # Initialize values
    self.comment = None
    
    # Parse the header
    self.parseHeader(offset)

  def parseHeader(self, offset):
    is_jpeg = True
    
    # Read the header
    data = self.fp.read(2)
    if (data != "\xff\xd8"):
      is_jpeg = False
    
    # Map the different fields. The key is the type of field, the value is a
    # list of [offset in file, length in bytes].
    self.segments = {}
  
    while (data != "") and (is_jpeg):
      data = self.fp.read(2)
      
      # Each segment (SOI, APP1, APP2, EOI, etc) in a JPEG file starts with the
      # byte FF, with the following byte specifying which field it is.
      if (data[0] != "\xff"):
        is_jpeg = False
      if ((data[1] == '\xd9') or (data[1] == '\xda')): # SOS and EOI
        break
      part_type = convBytes2Int(data[1], self.is_be)
      
      # The lenght of the part is determined in the following two bytes, and
      # these are included in the length.
      part_len = convBytes2Int(self.fp.read(2), self.is_be)
      self.segments[part_type] = [self.fp.tell(), part_len]
      self.fp.seek(self.fp.tell() + part_len - 2)

    # Check for a JPEG Comment
    if (254 in self.segments):
      self.fp.seek(self.segments[254][0])
      self.comment = self.fp.read(self.segments[254][1] - 2)
      
    # Seek to APP1, where the Exif data is stored
    if (225 in self.segments) and (is_jpeg):
      app1_offset = self.segments[225][0]
      self.fp.seek(app1_offset)
      data = self.fp.read(6)
      if (data != "Exif\x00\x00"):
        is_jpeg = False
      else:
        tiff_block = tiff.Tiff(self.fp, self.fp.tell())
        self.ifds = tiff_block.ifds
        self.iptc_info = tiff_block.iptc_info
    
    # If the IPTC info wasn't encoded in the Tiff IFD, we can look for it in
    # APP13 (Photoshop data) (0xED)
    if (not self.iptc_info) and (237 in self.segments): 
      self.fp.seek(self.segments[237][0])
      if (self.fp.read(24) == "Photoshop 3.0\x008BIM\x04\x04\x00\x00\x00\x00"): # FIXME: I don't understand these Photosop 8BIM structures, if only IPTC info is present in APP13, the header looks like this.
        self.iptc_info = iptc.IPTC(self.fp, self.fp.tell() + 2, convBytes2Int(self.fp.read(2)))
          
    if not (is_jpeg):
      raise "File is not JPEG"
      
  def getComment(self):
    """ Return the file comment, or None if no comment was found. """
    return self.comment
