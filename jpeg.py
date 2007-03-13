import exif, tiff, metainfofile, iptc, byteform
#from helper import convBytes2Int

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

# The different kinds of segments and their numbers
SEGMENTS = ["APP0", "APP1", "APP2", "APP3", "APP4", "APP5", "APP6", "APP7", "APP8", "APP9", "APP10", "APP11", "APP12", "APP13", "APP14", "APP15", "COM", "DQT", "DRI", "DHT", "SOF0", "SOF1", "SOF2", "SOF3", "SOS", "EOI"]

SEG_NUMS = {
  "APP0":  0xE0,
  "APP1":  0xE1,
  "APP2":  0xE2,
  "APP3":  0xE3,
  "APP4":  0xE4,
  "APP5":  0xE5,
  "APP6":  0xE6,
  "APP7":  0xE7,
  "APP8":  0xE8,
  "APP9":  0xE9,
  "APP10": 0xEA,
  "APP11": 0xEB,
  "APP12": 0xEC,
  "APP13": 0xED,
  "APP14": 0xEE,
  "APP15": 0xEF,
  "COM":   0xFE,
  "DQT":   0xDB,
  "DRI":   0xDD,
  "DHT":   0xC4,
  "SOF0":  0xC0,
  "SOF1":  0xC1,
  "SOF2":  0xC2,
  "SOF3":  0xC3,
  "SOS":   0xDA,
  "EOI":   0xD9
}

class Segment:
  """ A class for managing JPEG segments. """
  
  def __init__(self, number, *args):
    """ The segment can be initialized in two forms:
        - With a file pointer and offset in this file to the start of the
          segment (the 0xFF0xXX part).
        - With a byte stream
        Furthermore, it needs to know it's one-byte number that specifies the
        segment type. """
    
    self.number = number
    
    # Test for either of two initialization forms
    if (len(args) == 2):
      # We have a position in the file
      self.fp, self.offset = args
      self.content = None
    elif (len(args) == 1):
      # We have  a user set value
      self.setContent(args[0])
    else:
      raise "Initialize a segment either with a byte stream or with a file pointer and offset!"
      
  def setContent(self, content):
    """ Set the content of the segment. """
    
    self.content = content
    
    # Invalidate the file stuff 
    self.fp      = None
    self.offset  = None
    
  def getContentLength(self):
    """ Return the length of the data in the segment. """
    
    # If we have user content, return that length
    if (self.content):
      return len(self.content)
      
    # Otherwise, read it from the segment
    else:
      self.fp.seek(self.offset + 2)
      return byteform.btoi(self.fp.read(2)) - 2
      
  def getContent(self, length = None):
    """ Return the content of the segment. """

    # Find out the length we should read
    seg_length = self.getContentLength()
    if (length):
      if (length > seg_length):
        length = seg_length
    else:
      length = seg_length
    
    # If we have user set content, return that
    if (self.content):
      return self.content[:length]
    # Otherwise, read the content from disk
    else:
      self.fp.seek(self.offset + 4)
      return self.fp.read(length)
    
  def getSegment(self):
    """ Return the complete segment, including headers. """
    
    byte_str = "\xff" + chr(self.number)
    content = self.getContent()
    byte_str += byteform.itob(len(content) + 2, 2)
    byte_str += content
      
    return byte_str
      
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
    
    # For each segment of a certain type, we keep a list in the self.segments
    # dict.
    self.segments = {}
    for seg_type in SEGMENTS:
      self.segments[SEG_NUMS[seg_type]] = []
    
    # Also remember the segments were we found the Exif and IPTC data
    self.exif_segment = None
    self.iptc_segment = None
    
    # Parse the header
    self.parseFile(offset)

  def parseFile(self, offset):
    is_jpeg = True
    
    # Read the header
    data = self.fp.read(2)
    if (data != "\xff\xd8"):
      is_jpeg = False

    # Read the file
    while (data != "") and (is_jpeg):
      data = self.fp.read(2)
      
      # Each segment (SOI, APP1, APP2, EOI, etc) in a JPEG file starts with the
      # byte FF, with the following byte specifying which field it is.
      if (data[0] != "\xff"):
        raise "File is not JPEG"
        
      part_type = byteform.btoi(data[1], big_endian = self.is_be)
      # Create a new segment, with the current file offset, -2 to incluse
      # the segment header
      segment = Segment(part_type, self.fp, self.fp.tell() - 2)
      self.segments[part_type].append(segment)
      
      # At the Scan Header, the segment structure stops, and so should we 
      if (part_type == SEG_NUMS["SOS"]):
        break
        
      # Otherwise, seek to the next segment.
      # WARNING: the value needs to be absolute, because the Segment class does
      # some file seeking too! The 2 is for the 2 bytes specifying the segment
      # length.
      else:          
        self.fp.seek(segment.offset + segment.getContentLength() + 4) 
    
    # Try to find the Exif data. It should be in one off the APP1 segments,
    # marked by "Exif\x00\x00"
    for seg in self.segments[SEG_NUMS["APP1"]]:
      if (seg.getContent(6) == "Exif\x00\x00"):
        self.exif_segment = seg
        tiff_block = tiff.Tiff(self.fp, seg.offset + 10) # 4 bytes segment header + Exif marker
        self.ifds = tiff_block.ifds
        self.iptc_info = tiff_block.iptc_info
        break

    # If the IPTC info wasn't encoded in the Tiff IFD, we can look for it in
    # APP13 (Photoshop data) (0xED)
    if (not self.iptc_info):
      for seg in self.segments[SEG_NUMS["APP13"]]:
        if (seg.getContent(24) == "Photoshop 3.0\x008BIM\x04\x04\x00\x00\x00\x00"): # FIXME: I don't understand these Photosop 8BIM structures, if only IPTC info is present in APP13, the header looks like this.
          self.iptc_info = iptc.IPTC(self.fp, seg.offset + 30, seg.getContentLength())
  
  def writeFile(self, file_path):
    # Open the new file for writing
    out_fp = file(file_path, "w")
    out_fp.write("\xff\xd8")
    
    # Prepare the Exif segment for writing
    # Write the Exif header
    byte_str = "Exif\x00\x00"
    
    # Construct the Tiff header
    ifd_is_be = self.ifds["tiff"].is_be
    if (ifd_is_be):
      byte_str += "\x4d\x4d"
    else:
      byte_str += "\x49\x49"
    byte_str += byteform.itob(42, 2, big_endian = ifd_is_be)
    byte_str += byteform.itob(8, 4, big_endian = ifd_is_be)
    byte_str += self.getExifData()
    
    # Put the Exif data into an appropriate APP1 segment.  FIXME: This
    # invalidates that segment for feature data extraction.
    #if (not self.exif_segment):
    #  self.exif_segment = Segment(SEG_NUMS[APP1], byte_str)
    #  self.segments[SEG_NUMS[APP1]].append(self.exif_segment)
    #else:
    self.exif_segment.setContent(byte_str)
    
    # Iterate over all segments and copy them from the original file or rewrite
    # them.
    for seg_type in SEGMENTS:
      seg_num = SEG_NUMS[seg_type]
      for segment in self.segments[seg_num]:
        #print seg_num, segment.number
        # Write the start of the segment
        out_fp.write(segment.getSegment())
        
    # Write the image data, which starts after the SOS segment
    segment = self.segments[SEG_NUMS["SOS"]][-1]
    self.fp.seek(segment.offset + segment.getContentLength() + 2)
    out_fp.write(self.fp.read())
    
    out_fp.close()
    
  def getComments(self):
    """ Return a list with the file comments, or None if no comment was found.
    """

    # Loop over the comment segments 
    comments = []
    for com_seg in self.segments[SEG_NUMS["COM"]]:
      comments.append(com_seg.getContent())

    # Return None if no comment was found, or a list with comments otherwise      
    if (len(comments) == 0):
      return None
    else:
      return comments
    
  def setComment(self, comment, append = False):
    """ Set the JPEG comment. If append is True, the comment will be recorded as
        an additional COM segment. """
    segment = Segment(SEG_NUMS["COM"], comment)
    if (append):
      self.segments[SEG_NUMS["COM"]].append(segment)
    else:
      self.segments[SEG_NUMS["COM"]] = [segment]
