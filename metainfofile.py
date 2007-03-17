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

import byteform, tag

class Photoshop(tag.Tag):
  """ Read and write the photoshop structure. """
  
  def __init__(self, *args, **kwargs):
    """ Initialize the structure. It may be done by passing an open file object,
        offset to the start of the structure, and length, or by passing the
        binary content as string. An optional big_endian argument may be given
        to determine the byte ordering (defaults to big endian). """
      
    # Check for the endiannnes parameter
    if ("big_endian" in kwargs): self.big_endian = kwargs["big_endian"]
    else: self.big_endian = True
    
    # Find out in which form we were called and set the parameters correct for
    # the Tag constructor
    base_kwargs = {}
    if (len(args) == 1):
      base_kwargs[data] = args[0]
    elif (len(args) == 3):
      base_kwargs["fp"]     = args[0]
      base_kwargs["offset"] = args[1]
      base_kwargs["length"] = args[2]
      
    # Call the Tag constructor
    tag.Tag.__init__(self, **base_kwargs)
    
    # Parse the structure
    self.tags = {}
    self.parse()
    
  def parse(self):
    """ Parse the structure. """
    
    while (self.byte_pos < self.length):
      # The first four bytes of a data structure should always be the ASCII
      # string 8BIM
      data = self.read(4)
      if (data != "8BIM"):
        break

      # The next two bytes specify the resource ID (tag number)
      tag_num = byteform.btoi(self.read(2), big_endian = self.big_endian)
        
      # What then follows is the "Pascal string". The first byte determines its
      # length. If the total is an uneven number, it is padded with a \x00
      # character. We don't need this string, so we step over it. 
      ps_len =  byteform.btoi(self.read(1), big_endian = self.big_endian)
      if ((ps_len % 2) == 0):
        ps_len += 1
      self.read(ps_len)
        
      # Now it's getting interesting; the next four bytes determine the length
      # of the data
      data_len = byteform.btoi(self.read(4), big_endian = self.big_endian)
       
      # Store the byte position and data length in the tags dict
      self.tags[tag_num] = tag.Tag(self.fp, self.byte_pos, data_len)
      
      # Skip to the next structure
      self.read(data_len)


  def setTag(self, tag_num, data):
    """ Set the tag_num to data. """
    
    self.tags[tag_num] = tag.Tag(data = data)
    
  def getDataBlock(self):
    """ Return the Photoshop structure as a binary data block. """

    # Store the buffer as string    
    out_str = ""
    
    # Iterate over all tags
    for tag_num in self.tags:
      tag = self.tags[tag_num]
      
      # Every data structure starts with "8BIM"
      out_str += "8BIM"
      
      # The next two bytes specify the resource ID (tag number)
      out_str += byteform.itob(tag_num, 2, big_endian = self.big_endian)
        
      # Then we get the Pascal string, which we simply set to nothing
      out_str += "\x00\x00"
           
      # Encode the length of the data
      out_str += byteform.itob(tag.getDataLength(), 4, big_endian = self.big_endian)
       
      # And append the data itself
      out_str += tag.getData()
      
    return out_str
        
class MetaInfoFile:
  """The base class for files containing meta information."""
  
  def __init__(self):
    self.ifds = dict.fromkeys(["tiff", "exif", "gps"], None)
    self.iptc_info = None

  def getExifTagPayload(self, tag):
    """ Return the payload of a tag with the specified name. """
    
    payload = None
    
    # Iterate over all IFD's
    for ifd in ['tiff', 'exif', 'gps']:
      if (self.ifds[ifd]):
        payload = self.ifds[ifd].getTagPayload(tag)
        if payload:
          break

    return payload

  def getExifBlock(self):
    """ Return the encoded Tiff, Exif and GPS IFD's as a block. """
    
    # The exif data can have a different endianness than the JPEG file
    ifd_big_endian = self.ifds["tiff"].big_endian
          
    # Calculate the different byte offsets (within the segment)
    if "exif" in self.ifds:
      exif_ifd_offset = self.ifds["tiff"].getSize() + 8 # 8 for Tiff header
    else:
      exif_ifd_offset = 0
      
    if "gps" in self.ifds:
      gps_ifd_offset  = exif_ifd_offset + self.ifds["exif"].getSize()
    else:
      gps_ifd_offset = 0

    if "interop" in self.ifds:
      interop_ifd_offset  = gps_ifd_offset + self.ifds["gps"].getSize() # FIXME: If no GPS block is present, this will produce the wrong result. This is also the case for other parts
    else:
      interop_ifd_offset = 0
      
    # Set the offsets to the tiff data
    if (exif_ifd_offset):
      self.ifds["tiff"].setTagPayload("Exif IFD Pointer", exif_ifd_offset)
    if (gps_ifd_offset):
      self.ifds["tiff"].setTagPayload("GPSInfo IFD Pointer", gps_ifd_offset)

    # Set the offsets to the exif data. FIXME: Check for presence of Exif data first
    if (interop_ifd_offset):
      self.ifds["exif"].setTagPayload(40965, interop_ifd_offset)

    # Write the Exif IFD's
    byte_str = self.ifds["tiff"].getByteStream(8)
    if ("exif" in self.ifds):
      byte_str += self.ifds["exif"].getByteStream(exif_ifd_offset)
    if ("gps" in self.ifds):
      byte_str += self.ifds["gps"].getByteStream(gps_ifd_offset)
    if ("interop" in self.ifds):
      byte_str += self.ifds["interop"].getByteStream(interop_ifd_offset)
      
    return byte_str
    
  def getIPTCBlock(self):
    """ Return the encoded IPTC data as a blcok. """
    pass
