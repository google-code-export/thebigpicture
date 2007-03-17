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
import ifd, exif, iptc, metainfofile, byteform

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
      self.fp = file(file_indicator)
    elif (type(file_indicator) == types.FileType):
      self.fp = file_indicator
    else:
      raise "No valid file parameter given -- file path or file object needed." 
      
    # Parse the header
    self.parseFile(offset)
      
  def parseFile(self, offset):
    """Parse the header of the Tiff file, starting ot the byte offset.""" 
    is_tiff = False
    self.fp.seek(offset)
    
    # Read the header
    data = self.fp.read(2)
    if (data == "MM"):
      self.big_endian = True
      is_tiff = True
    elif (data == "II"):
      self.big_endian = False
      is_tiff = True
      
    # The next two bytes should be 42
    if (is_tiff) and (byteform.btoi(self.fp.read(2), big_endian = self.big_endian) == 42):
      is_tiff = True
      
    # If the file does not have a Tiff header, report it as false 
    if not(is_tiff):
      raise "File is not Tiff"
    
    # Map all the IFD's
    
    # Get the first IFD (The "Tiff" tags)
    ifd_offsets = {}
    ifd_offsets["tiff"] = byteform.btoi(self.fp.read(4), big_endian = self.big_endian)
    self.ifds["tiff"] = exif.TIFF(self.fp, ifd_offsets["tiff"], offset, self.big_endian)
    
    # Get the Exif tags
    ifd_offsets["exif"] = self.ifds["tiff"].getTagPayload("Exif IFD Pointer")
    if (ifd_offsets["exif"]):
      self.ifds["exif"] = exif.Exif(self.fp, ifd_offsets["exif"], offset, self.big_endian)
      
    # Get the GPS tags
    ifd_offsets["gps"] = self.ifds["tiff"].getTagPayload("GPSInfo IFD Pointer")
    if (ifd_offsets["gps"]):
      self.ifds["gps"] = exif.GPS(self.fp, ifd_offsets["gps"], offset, self.big_endian)

    # Get the IPTC block. The payload isn't the position in the file, but
    # rather the IPTC content. To let the IPTC class do its job, we feed it
    # the position of the block.
    if (33723 in self.ifds["tiff"].fields):
      iptc_offset = self.ifds["tiff"].fields[33723][0]
      iptc_length = self.ifds["tiff"].fields[33723][2]
      self.iptc_info = iptc.IPTC(self.fp, iptc_offset, iptc_length) 
    else:
      self.iptc_info = None
      
    #self.fp.seek(self.ifd_offsets["ifd0"] + self.ifds["ifd0"].getSize())
    #data = convBytes2Int(self.fp.read(4))
    #if (data != 0):
    #  self.ifd_offsets["ifd1"] = data
    #  self.ifds["ifd1"] = ifd.IFD(self.fp, self.ifd_offsets["ifd1"], self.big_endian)
    
  def writeFile(self, file_path):
    out_fp = file(file_path, "w")
    if (self.big_endian):
      out_fp.write("\x4d\x4d")
    else:
      out_fp.write("\x49\x49")
    out_fp.write(byteform.itob(42, 2, big_endian = self.big_endian))
    out_fp.write(byteform.itob(8, 4, big_endian = self.big_endian))
    
    exif_ifd_offset = self.ifds["tiff"].getSize() + 8
    gps_ifd_offset  = exif_ifd_offset + self.ifds["exif"].getSize()

    self.ifds["tiff"].setTagPayload("Exif IFD Pointer", exif_ifd_offset)
    self.ifds["tiff"].setTagPayload("GPSInfo IFD Pointer", gps_ifd_offset)
    
    out_fp.write(self.ifds["tiff"].getByteStream(8))
    out_fp.write(self.ifds["exif"].getByteStream(exif_ifd_offset))
    out_fp.write(self.ifds["gps"].getByteStream(gps_ifd_offset))
    out_fp.close()
