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

import ifd, qdb, datablock, byteform

class CanonIFD(ifd.IFD):
  tags = qdb.QDB()
  tags.addList("name", [])
  tags.addList("num", [])
  tags.addList("data_type", [])
  tags.addList("count", [])

class FujifilmIFD(ifd.IFD):
  tags = qdb.QDB()
  tags.addList("name", [])
  tags.addList("num", [])
  tags.addList("data_type", [])
  tags.addList("count", [])

  def __init__(self, file_pointer = None, ifd_offset = 0, header_offset = 0, data = None, big_endian = False):
    # Fujifilm always uses little endian
    block = datablock.DataBlock(fp = file_pointer, offset = ifd_offset + header_offset, data = data)
    header = block.read(8)
    if (header == None):
      mn_offset = 0
    elif (header == "FUJIFILM"):
      mn_offset = byteform.btousi(block.read(4), big_endian = False)
    else:
      raise "No valid Fujifilm Makernote!"
      
    ifd.IFD.__init__(self, file_pointer, mn_offset, ifd_offset + header_offset, data, big_endian = False)
    
  def getBlob(self, offset, next_ifd = 0):
    ret_str = "FUJIFILM"
    ret_str += byteform.itob(12, 4, big_endian = self.big_endian)
    ret_str += ifd.IFD.getBlob(self, 12, next_ifd)
    return ret_str

class IFDWithHeader(ifd.IFD):
  """ Base class for Makenote IFD's which have an exra header. Derived classes
      should set two parameters:
      - header_str:    The header string.
      - header_length: The length of the header. This may be more than the 
                       length of the header string, if that contains extra info.
  """
  
  def __init__(self, file_pointer = None, ifd_offset = 0, header_offset = 0, data = None, big_endian = True):
    # Create a temporary Datablock to parse the data
    block = datablock.DataBlock(fp = file_pointer, offset = ifd_offset, data = data)
    
    # Read the header string
    header = block.read(len(self.header_str))
    if (header != self.header_str) and (header != ""):
      raise "No valid Makernote!"
      
    # Read the rest of the header and save it for writing
    self.extra_bytes = block.read(self.header_length - len(self.header_string))
    
    # Initialize the IFD
    ifd.IFD.__init__(self, file_pointer, ifd_offset + self.header_length, header_offset, data, big_endian)

  def getBlob(self, offset, next_ifd = 0):
    """ Simple modified writeBlob, which writes the header string and the saved
        rest of the header, followed by the data. """
        
    ret_str = header_str
    ret_str += ifd.IFD.getBlob(self, offset, next_ifd)
    return ret_str

class MinoltaIFD(ifd.IFD):
  tags = qdb.QDB()
  tags.addList("name", [])
  tags.addList("num", [])
  tags.addList("data_type", [])
  tags.addList("count", [])

  def __init__(self, file_pointer = None, ifd_offset = 0, header_offset = 0, data = None, big_endian = True):
    # Minolta always uses big endian
    ifd.IFD.__init__(self, file_pointer, ifd_offset, header_offset, data, big_endian = True)
    
class OlympusIFD(IFDWithHeader):
  header_str    = "OLYMP\x00"
  header_length = 10
  
  tags = qdb.QDB()
  tags.addList("name", [])
  tags.addList("num", [])
  tags.addList("data_type", [])
  tags.addList("count", [])

class SigmaIFD(ifd.IFD):
  header_str    = "SIGMA\x00\x00\x00"
  header_length = 10
  
  tags = qdb.QDB()
  tags.addList("name", [])
  tags.addList("num", [])
  tags.addList("data_type", [])
  tags.addList("count", [])

class FoveonIFD(ifd.IFD):
  header_str    = "FOVEON\x00\x00"
  header_length = 10
  
  tags = qdb.QDB()
  tags.addList("name", [])
  tags.addList("num", [])
  tags.addList("data_type", [])
  tags.addList("count", [])

class PanasonicIFD(ifd.IFD):
  header_str    = "Panasonic\x00\x00\x00"
  header_length = 12
  
  tags = qdb.QDB()
  tags.addList("name", [])
  tags.addList("num", [])
  tags.addList("data_type", [])
  tags.addList("count", [])
  
  def getBlob(self, offset, next_ifd = 0):
    ret_str = header_str
    ret_str += ifd.IFD.getBlob(self, offset, None) # Panasonic does not write a next IFD pointer
    return ret_str
    
  def getSize(self):
    return ifd.IFD.getSize(self, False)
