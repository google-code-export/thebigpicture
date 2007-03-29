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

import datablock, byteform

# TODO: Convert to metainfofile.MetaInfoSegement etc. structure

class Photoshop(datablock.DataBlock):
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
    datablock.DataBlock.__init__(self, **base_kwargs)
    
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
      self.tags[tag_num] = datablock.DataBlock(self.fp, self.byte_pos, data_len)
      
      # Skip to the next structure
      self.read(data_len)


  def setTag(self, tag_num, data):
    """ Set the tag_num to data. """
    
    self.tags[tag_num] = datablock.DataBlock(data = data)
    
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
