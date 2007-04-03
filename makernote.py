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

  def __init__(self, file_pointer = None, ifd_offset = 0, header_offset = 0, data = None, big_endian = big_endian):
    # Fujifilm always uses little endian
    block = datablock.DataBlock(fp = file_pointer, offset = ifd_offset, data = data)
    if (block.read(8) != "FUJIFILM"):
      raise "No valid Fujifilm Makernote!"
    
    mn_offset = byteform.btoi(block.read(4), big_endian = False)
    ifd.IFD.__init__(self, file_pointer, mn_offset, ifd_offset, data, big_endian = False)

class IFDWithHeader(ifd.IFD):
  def __init__(self, file_pointer = None, ifd_offset = 0, header_offset = 0, data = None, big_endian = big_endian):
    block = datablock.DataBlock(fp = file_pointer, offset = ifd_offset, data = data)
    if (block.read(len(self.header_str)) != self.header_str):
      raise "No valid Makernote!"
    
    ifd.IFD.__init__(self, file_pointer, ifd_offset + self.header_length, header_offset, data, big_endian)
  
class MinoltaIFD(ifd.IFD):
  tags = qdb.QDB()
  tags.addList("name", [])
  tags.addList("num", [])
  tags.addList("data_type", [])
  tags.addList("count", [])

  def __init__(self, file_pointer = None, ifd_offset = 0, header_offset = 0, data = None, big_endian = big_endian):
    # Minolta always uses big endian
    ifd.IFD.__init__(self, file_pointer, ifd_offset, header_offset, data, big_endian = True)
    
class OlympusIFD(IFDWithHeader):
  header_str    = "OLYMP\x00"
  header_length = 6
  
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
