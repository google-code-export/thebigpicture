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

# Import local classes
import ifd, exif, metainfofile, byteform, iptcnaa

# Import python modules
import types

class Tiff(metainfofile.MetaInfoFile):
  def __init__(self, file_indicator, offset = 0):
    """Initialize a Tiff file object. It needs an open file object or a path to
    a file on the disk. A byte offset may be given to the start of the Tiff
    header."""
    
    metainfofile.MetaInfoFile.__init__(self)
    
    # Initialize the file pointer
    if (type(file_indicator) == types.StringType):
      self.fp = open(file_indicator, "rb")
    elif (type(file_indicator) == types.FileType):
      self.fp = file_indicator
    else:
      raise "No valid file parameter given -- file path or file object needed." 
    
    self.offset = offset
    
    # Parse the header
    self.parseHeader()
      
  def parseHeader(self):
    """Parse the header of the Tiff file, starting ot the byte offset."""
    
    is_tiff = False
    self.fp.seek(self.offset)
    
    # Read the header
    data = self.fp.read(2)
    if (data == "MM"):
      self.big_endian = True
      is_tiff = True
    elif (data == "II"):
      self.big_endian = False
      is_tiff = True
      
    # The next two bytes should be 42
    if (is_tiff) and (byteform.btousi(self.fp.read(2), big_endian = self.big_endian) == 42):
      is_tiff = True
      
    # If the file does not have a Tiff header, report it as false 
    if not(is_tiff):
      raise "File is not Tiff"
    
    # Locate the Exif data
    self.exif_offset = byteform.btousi(self.fp.read(4), big_endian = self.big_endian)
    
  def loadExif(self):
    # Read the Exif data
    self.exif = exif.Exif(self.fp, self.exif_offset, self.offset, self.big_endian)

  def loadIPTC(self):
    # Get the IPTC block. The paylaod should simply be the encoded IPTC data
    # (datatype UNDEFINED or BYTE), but in reality it often is set as long,
    # where the number points to the absolute offset in the file. We have to
    # work around this restricition.
    # (see http://www.awaresystems.be/imaging/tiff/tifftags/iptc.html for more 
    # information.)
    
    tiff_record = self.__getExif__().getRecord(1)
    if (tiff_record):
      try:
        iptc_tag = tiff_record.fields[33723]
        iptc_offset = iptc_tag.getDataOffset()
        #iptc_length = iptc_tag.getDataLength()
        self.iptc = iptcnaa.IPTC(self.fp, iptc_offset) 
      except KeyError:
        pass
    
    # If we failed to load IPTC data, create an empty IPTC object
    if (self.iptc == None):
      self.iptc = iptcnaa.IPTC()
          
  def writeFile(self, file_path):
    # Write the header
    out_fp = open(file_path, "wb")
    if (self.big_endian):
      out_fp.write("\x4d\x4d")
    else:
      out_fp.write("\x49\x49")
    out_fp.write(byteform.itob(42, 2, big_endian = self.big_endian))
    out_fp.write(byteform.itob(8, 4, big_endian = self.big_endian))
    
    # Embed the IPTC data in the Exif structure
    if (self.iptc):
      self.exif.setTag(33723, self.iptc.getBlob(), record = 1)
      
    # Save the old strip offsets before we overwrite it
    old_strip_offsets = self.__getExif__().getTag("StripOffsets", 1)

    # Restructure the Exif metadata to contain the new strip offsets
    curr_offset = self.exif.getSize() + 8 # 8 bytes for the Tiff header
    tiff = self.exif.getRecord(1)
    strip_lengths = self.exif.getTag("StripByteCounts", 1)
    new_strip_offsets = []
    for length in strip_lengths:
      new_strip_offsets.append(curr_offset)
      curr_offset += length
    self.exif.setTag("StripOffsets", new_strip_offsets, 1)

    # Write the Exif data
    out_fp.write(self.exif.getBlob(8))
    
    # Write the image data
    for strip_num in range(len(strip_lengths)):
      offset = old_strip_offsets[strip_num]
      length = strip_lengths[strip_num]
      self.fp.seek(offset)
      out_fp.write(self.fp.read(length))
      
    out_fp.close()
