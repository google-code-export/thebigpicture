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
SEGMENTS = ["APP0", "APP1", "APP2", "APP3", "APP4", "APP5", "APP6", "APP7", "APP8", "APP9", "APP10", "APP11", "APP12", "APP13", "APP14", "APP15", "DQT", "DRI", "DHT", "SOF0", "SOF1", "SOF2", "SOF3", "SOS", "EOI", "COM"]

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
  "DQT":   0xDB,
  "DRI":   0xDD,
  "DHT":   0xC4,
  "SOF0":  0xC0,
  "SOF1":  0xC1,
  "SOF2":  0xC2,
  "SOF3":  0xC3,
  "SOS":   0xDA,
  "EOI":   0xD9,
  "COM":   0xFE
}

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
        break
        
      part_type = byteform.btoi(data[1], big_endian = self.is_be)
      if (part_type == SEG_NUMS["SOS"]):
        self.segments[part_type] = [self.fp.tell(), None]
        break
      elif (part_type == SEG_NUMS["EOI"]):
        break
      else:
        # The lenght of the part is determined in the following two bytes, and
        # these are included in the length.
        part_len = byteform.btoi(self.fp.read(2), big_endian = self.is_be)
        self.segments[part_type] = [self.fp.tell(), part_len] # FIXME: reading [1] bytes from [0] reads two bytes too many
        self.fp.seek(self.fp.tell() + part_len - 2)
    
    # Check for a JPEG Comment
    if (254 in self.segments):
      self.fp.seek(self.segments[254][0])
      self.comment = self.fp.read(self.segments[254][1] - 2)
      
    # Seek to APP1, where the Exif data is stored
    self.iptc_info = None
    if (SEG_NUMS["APP1"] in self.segments) and (is_jpeg):
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
    if (not self.iptc_info) and (SEG_NUMS["APP13"] in self.segments): 
      self.fp.seek(self.segments[237][0])
      if (self.fp.read(24) == "Photoshop 3.0\x008BIM\x04\x04\x00\x00\x00\x00"): # FIXME: I don't understand these Photosop 8BIM structures, if only IPTC info is present in APP13, the header looks like this.
        self.iptc_info = iptc.IPTC(self.fp, self.fp.tell() + 2, byteform.btoi(self.fp.read(2)))
          
    if not (is_jpeg):
      raise "File is not JPEG"
      
  def writeFile(self, file_path):
    # Open the new file for writing
    out_fp = file(file_path, "w")
    out_fp.write("\xff\xd8")
    
    # Iterate over all segments and copy them from the original file or rewrite
    # them
    for segment in SEGMENTS:
      segment_num = SEG_NUMS[segment]
      if segment_num in self.segments:
        
        # Write the start of the segment
        out_fp.write("\xff")
        out_fp.write(byteform.itob(segment_num, 1))
        
        if (segment_num == SEG_NUMS["APP1"]):
          # Write the Exif segment
          
          # The exif data can have a different endianness than the JPEG file
          ifd_is_be = self.ifds["tiff"].is_be
          
          # Calculate the different byte offsets (within the segment)
          exif_ifd_offset = self.ifds["tiff"].getSize() + 8 # 8 for Tiff header
          gps_ifd_offset  = exif_ifd_offset + self.ifds["exif"].getSize()
          
          # Set the offsets to the tiff data
          self.ifds["tiff"].setTagPayload("Exif IFD Pointer", exif_ifd_offset)
          self.ifds["tiff"].setTagPayload("GPSInfo IFD Pointer", gps_ifd_offset)
          
          # Write the Exif header
          # The length is the sum of the Exif fields, plus 2 bytes specifying
          # the length off the segment, plus 6 bytes for the Exif header, plus
          # 8 bytes for the Tiff header
          length = self.ifds['tiff'].getSize() + self.ifds['exif'].getSize() + self.ifds['gps'].getSize() + 16
          out_fp.write(byteform.itob(length, 2, big_endian = self.is_be))
          out_fp.write("Exif\x00\x00")
          
          # Write the Tiff header
          if (ifd_is_be):
            out_fp.write("\x4d\x4d")
          else:
            out_fp.write("\x49\x49")
          out_fp.write(byteform.itob(42, 2, big_endian = ifd_is_be))
          out_fp.write(byteform.itob(8, 4, big_endian = ifd_is_be))
          
          # Write the Exif IFD's
          out_fp.write(self.ifds["tiff"].getByteStream(8))
          out_fp.write(self.ifds["exif"].getByteStream(exif_ifd_offset))
          out_fp.write(self.ifds["gps"].getByteStream(gps_ifd_offset))
        elif (segment_num == SEG_NUMS["SOS"]):
          # Write the actual image data and EOI
          self.fp.seek(self.segments[segment_num][0])
          out_fp.write(self.fp.read())
        else:
          # Copy the segment literally from the original file
          out_fp.write(byteform.itob(self.segments[segment_num][1], 2))
          self.fp.seek(self.segments[segment_num][0])
          out_fp.write(self.fp.read(self.segments[segment_num][1] - 2))

    out_fp.close()
    
  def getComment(self):
    """ Return the file comment, or None if no comment was found. """
    return self.comment
