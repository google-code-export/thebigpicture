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

# Import the custom modules
import exif, tiff, metainfofile, byteform, datablock, iptcnaa, photoshop
# Import standard Python modules
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

# The different kinds of segments that can be load and written before the
# image data
SEGMENTS = ["APP0", "APP1", "APP2", "APP3", "APP4", "APP5", "APP6", "APP7",
            "APP8", "APP9", "APP10", "APP11", "APP12", "APP13", "APP14",
            "APP15", "COM", "DQT", "DHT", "DAC", "DRI"]

#EXIF = [soi, app1, app2, dqt, dht, dri, sof, sos, eoi]
#jfif = [soi, app0[0-n], sof[0-m], eoi]

SEG_NUMS = {
  "SOF0":  0xC0, # 192
  "SOF1":  0xC1, # 193
  "SOF2":  0xC2, # 194
  "SOF3":  0xC3, # 195
  "DHT":   0xC4, # 196
  "SOF5":  0xC5, # 197
  "SOF6":  0xC6, # 198
  "SOF7":  0xC7, # 199
  "JPG":   0xC8, # 200
  "SOF9":  0xC9, # 201
  "SOF10": 0xCA, # 202
  "SOF11": 0xCB, # 203
  "DAC":   0xCC, # 204
  "SOF13": 0xCD, # 205
  "SOF14": 0xCE, # 206
  "SOF15": 0xCF, # 207
  "RST0":  0xD0, # 208
  "RST1":  0xD1, # 209
  "RST2":  0xD2, # 210
  "RST3":  0xD3, # 211
  "RST4":  0xD4, # 212
  "RST5":  0xD5, # 213
  "RST6":  0xD6, # 214
  "RST7":  0xD7, # 215
  "SOI":   0xD8, # 216
  "EOI":   0xD9, # 217
  "SOS":   0xDA, # 218
  "DQT":   0xDB, # 219
  "DNL":   0xDC, # 220
  "DRI":   0xDD, # 221
  "DHP":   0xDE, # 222
  "EXP":   0xDF, # 223
  "APP0":  0xE0, # 224
  "APP1":  0xE1, # 225
  "APP2":  0xE2, # 226
  "APP3":  0xE3, # 227
  "APP4":  0xE4, # 228
  "APP5":  0xE5, # 229
  "APP6":  0xE6, # 230
  "APP7":  0xE7, # 231
  "APP8":  0xE8, # 232
  "APP9":  0xE9, # 233
  "APP10": 0xEA, # 234
  "APP11": 0xEB, # 235
  "APP12": 0xEC, # 236
  "APP13": 0xED, # 237
  "APP14": 0xEE, # 238
  "APP15": 0xEF, # 239
  "JPG0":  0xF0, # 240
  "JPG1":  0xF1, # 241
  "JPG2":  0xF2, # 242
  "JPG3":  0xF3, # 243
  "JPG4":  0xF4, # 244
  "JPG5":  0xF5, # 245
  "JPG6":  0xF6, # 246
  "JPG7":  0xF7, # 247
  "JPG8":  0xF8, # 248
  "JPG9":  0xF9, # 249
  "JPG10": 0xFA, # 250
  "JPG11": 0xFB, # 251
  "JPG12": 0xFC, # 252
  "JPG13": 0xFD, # 253
  "COM":   0xFE  # 254
}

class Segment(datablock.DataBlock):
  """ A class for managing JPEG segments. """
  
  def __init__(self, *args, **kwargs):
    """ The segment can be initialized in three forms:
        - With a file pointer and offset in this file to the start of the
          segment (the 0xFF 0xXX part).
        - With a data stream
        - With a segment number
    """
    
    if ("big_endian" in kwargs): self.big_endian = kwargs["big_endian"]
    else: self.big_endian = True
      
    # There are four different ways in which this class can be initialized, but
    # it should always be with one or two arguments
    if (len(args) not in [1, 2]):
      raise "Segment class wasn't initialized properly!"
      
    # We construct a separate dict for the DataBlock arguments
    base_kwargs = {}
    
    # Check the different initialization types
    if (type(args[0]) == types.IntType):
      # Initialized with tag num
      self.number = args[0]
      if (len(args) == 2):
        base_kwargs["data"] = args[1]
        
    elif (type(args[0]) == types.StringType):
      # Initialized with data string. FIXME: What about file pointer initialization?
      self.number, length = self.__parseHeader__(args[0][:4])
      base_kwargs["data"] = args[0][4:length + 4] # Skip first four bytes of segment header
      
    elif (type(args[0]) == types.FileType):
      # Initialized with file pointer
      
      # Parse the header
      fp, offset = args[0:2]
      fp.seek(offset)
      self.number, length = self.__parseHeader__(fp.read(4))
      
      # Construct the data for tag init
      base_kwargs["fp"]     = fp
      base_kwargs["offset"] = offset + 4 # Data starts four bytes after segment
      base_kwargs["length"] = length
    
    # Call the Tag constructor
    datablock.DataBlock.__init__(self, **base_kwargs)
    
  def __parseHeader__(self, header):
    """ Parse the first bytes of the segment header, and return a list of number
        and length. """

    # The first byte of a JPEG segment header should be 0xFF
    if (header[0] != "\xFF"):
      raise "Not a JPEG segment!"
      
    # The next byte determines the type number of the segment      
    number = byteform.btousi(header[1], big_endian = self.big_endian)
    
    # The next two bytes determine the length of the segment. We subtract two
    # because it includes these two bytes.
    length = byteform.btousi(header[2:4], big_endian = self.big_endian) - 2
    
    return [number, length]
    
  def getNumber(self):
    return self.number
    
  def getBlob(self):
    """ Return the complete segment, including headers. """
    
    byte_str = "\xff" + chr(self.number)
    byte_str += byteform.itob(self.getDataLength() + 2, 2, big_endian = self.big_endian)
    content = self.getData()
    byte_str += content
      
    return byte_str
      
class Jpeg(metainfofile.MetaInfoFile):
  """Parse and write JPEG files."""

  # JPEG files are always big endian
  big_endian = True
    
  def __init__(self, file_indicator, offset = 0):
    """Initialize a JPEG file object. It needs an open file object or a path to
    a file on the disk. A byte offset may be given to the start of the JPEG
    header."""
    
    metainfofile.MetaInfoFile.__init__(self)
    
    # Initialize the file pointer
    if (type(file_indicator) == types.StringType):
      self.fp = open(file_indicator, "rb")
    elif (type(file_indicator) == types.FileType):
      self.fp = file_indicator
    else:
      raise "No valid file parameter given -- file path or file object needed." 
    
    # Initialize values
    self.comment      = None
    self.iptc_segment = None
    self.ps_info      = None
    self.exif_segment = None
    
    # For each segment of a certain type, we keep a list in the self.segments
    # dict.
    self.segments = {}
    for seg_type in SEGMENTS:
      self.segments[SEG_NUMS[seg_type]] = []
    
    # Also remember the segments were we found the Exif and IPTC data
    self.exif_segment = None
    self.iptc_segment = None
    self.ps_info      = None
    
    # Parse the header
    self.image_data_offset = None
    self.parseFile(offset)

  def parseFile(self, offset):
    is_jpeg = True
    
    # Read the header
    data = self.fp.read(2)
    if (data != "\xff\xd8"):
      is_jpeg = False

    # Read the file
    while (data != ""):
      curr_offset = self.fp.tell()
      segment = Segment(self.fp, curr_offset)
      part_type = segment.getNumber()
      
      # We read only until the start of the image data, which is at an SOF in
      # the case of normal and progressive Jpeg, and DHP in the case of 
      # hierarchical Jpeg
      if (part_type in [SEG_NUMS["SOF0"], SEG_NUMS["SOF1"], SEG_NUMS["SOF2"],
                        SEG_NUMS["SOF3"], SEG_NUMS["SOF5"], SEG_NUMS["SOF6"],
                        SEG_NUMS["SOF7"], SEG_NUMS["SOF9"], SEG_NUMS["SOF10"],
                        SEG_NUMS["SOF11"], SEG_NUMS["SOF13"], SEG_NUMS["SOF15"],
                        SEG_NUMS["DHP"]]):
        self.image_data_offset = curr_offset
        break
        
      # Otherwise, store the segment and seek to the next one.
      # WARNING: the value needs to be absolute, because the Segment class does
      # some file seeking too!
      else:
        self.segments[part_type].append(segment)
        self.fp.seek(segment.getDataOffset() + segment.getDataLength()) 
    
  def loadExif(self):
    """ Load the Exif data from the file. """
    
    # Try to find the Exif data. It should be in one off the APP1 segments,
    # marked by "Exif\x00\x00"
    for seg in self.segments[SEG_NUMS["APP1"]]:
      if (seg.read(6, 0) == "Exif\x00\x00"):
        self.exif_segment = seg
        tiff_block = tiff.Tiff(self.fp, seg.getDataOffset() + 6) # 6 bytes Exif marker
        tiff_block.loadExif()
        tiff_block.loadIPTC()
        self.exif = tiff_block.exif
        if (tiff_block.iptc.hasTags()): # FIXME: Dunno if this is actually possible
          self.iptc = tiff_block.iptc
        break

  def loadIPTC(self):
    """ Load the IPTC data from the file. """
    
    # If the IPTC info wasn't encoded in the Tiff IFD, we can look for it in
    # APP13 (Photoshop data) (0xED)
    if (self.iptc == None):
      for seg in self.segments[SEG_NUMS["APP13"]]:
        if (seg.read(14, 0) == "Photoshop 3.0\x00"):
          ps = photoshop.Photoshop(self.fp, self.fp.tell(), seg.getDataLength())
          if (1028 in ps.tags): # IPTC info is tag 1028
            self.iptc_segment = seg
            self.ps_info      = ps
            self.iptc = iptcnaa.IPTC(self.fp, ps.getDataOffset() + ps.tags[1028].getDataOffset(), ps.tags[1028].getDataLength())

    # If we didn't find IPTC info, create an empty object and the containing
    # structures
    if (self.iptc == None):
      self.iptc = iptcnaa.IPTC()

  def writeFile(self, file_path):
    # Open the new file for writing
    out_fp = open(file_path, "wb")
    out_fp.write("\xff\xd8")
    
    # Prepare the Exif segment for writing
    # Write the Exif header
    byte_str = "Exif\x00\x00"
    
    # Construct the Tiff header
    ifd_big_endian = self.__getExif__().big_endian
    if (ifd_big_endian):
      byte_str += "\x4d\x4d"
    else:
      byte_str += "\x49\x49"
    byte_str += byteform.itob(42, 2, big_endian = ifd_big_endian)
    byte_str += byteform.itob(8, 4, big_endian = ifd_big_endian)
    
    # Write the Exif data
    byte_str += self.__getExif__().getBlob(8)
    
    # Put the Exif data into an appropriate APP1 segment. FIXME: This
    # invalidates that segment for future data extraction.
    exif = self.__getExif__()
    if (exif.hasTags()):
      if (not self.exif_segment):
        self.exif_segment = Segment(SEG_NUMS[APP1], byte_str)
        self.segments[SEG_NUMS[APP1]].append(self.exif_segment)
      else:
        self.exif_segment.setData(byte_str)
    else:
      if (self.exif_segment):
        del self.segments[SEG_NUMS[APP1]][self.segments[SEG_NUMS[APP1]].index(self.exif_segment)]
        self.exif_segment = None
    
    # Prepare the IPTC segment for writing. FIXME: This
    # invalidates that segment for future data extraction.
    iptc = self.__getIPTC__()
    if (iptc.hasTags()):
      if (not self.iptc_segment):
        self.iptc_segment = Segment(SEG_NUMS["APP13"])
        self.segments[SEG_NUMS["APP13"]].append(self.iptc_segment)
      if (not self.ps_info):
        self.ps_info = photoshop.Photoshop()
      self.ps_info.setTag(1028, self.__getIPTC__().getBlob())
      self.iptc_segment.setData("Photoshop 3.0\x00" + self.ps_info.getDataBlock())
    # If we don't have any tags, remove the IPTC segment and Photoshop info
    else:
      if (self.iptc_segment):
        del self.segments[SEG_NUMS["APP13"]][self.segments[SEG_NUMS["APP13"]].index(self.iptc_segment)]
        self.iptc_segment = None
      if (self.ps_info):
        self.ps_info = None
    
    # Iterate over all segments and copy them from the original file or rewrite
    # them.
    for seg_type in SEGMENTS:
      seg_num = SEG_NUMS[seg_type]
      for segment in self.segments[seg_num]:
        # Write the segment
        out_fp.write(segment.getBlob())
        
    # Write the image data
    if (self.image_data_offset): # We only do the check here and not in the parsing, so we can still extract metadata from a broken image file
      self.fp.seek(self.image_data_offset)
      out_fp.write(self.fp.read())
    else:
      raise "Due to an error in the parsing of the file, it can not be written."
    
    out_fp.close()
    
  def getComments(self):
    """ Return a list with the file comments, or None if no comment was found.
    """

    # Loop over the comment segments 
    comments = []
    for com_seg in self.segments[SEG_NUMS["COM"]]:
      comments.append(com_seg.getData())

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
