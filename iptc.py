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
# along with The Big PictureGe; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
# 

import byteform

class IPTC:
  def __init__(self, fp, file_offset, size):
    self.fp          = fp
    self.file_offset = file_offset
    self.size        = size
    self.tags        = {}
    self.parse()
    
  def parse(self):
    self.fp.seek(self.file_offset)
    #length = convBytes2Int(self.fp.read(2))
    curr_byte = 0
    #while (curr_byte <= length):
    while ((self.fp.read(2) == "\x1c\x02") and (curr_byte < self.size)):
      tag_type = byteform.btoi(self.fp.read(1))
      length   = byteform.btoi(self.fp.read(2))
      if (tag_type in self.tags):
        self.tags[tag_type].append(self.fp.read(length))
      else:
        self.tags[tag_type] = [self.fp.read(length)]
        
      curr_byte += 3 + length
