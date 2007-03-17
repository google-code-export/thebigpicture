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

from byteform import *
import types, datatypes

class Digits(datatypes.DataType):
  """ The digits data type is a kind of ASCII data which only accepts numbers.
  """
  word_width = 1
  
  @classmethod
  def encode(cls, num, length = None, is_big_endian = True):
    """ Encode an integer number as string. The optional argument length
        specifies how many chars the output should occupy. """
    
    # Convert the number to string
    byte_str = str(num)
    
    # Optionally pad it with zeroes
    if (length != None):
      byte_str = (lenth - len(byte_str) * "0") + byte_str
      
    return byte_stream
    
  @classmethod
  def decode(cls, byte_stream, is_big_endian = True):
    """ Convert a string of numbers to a single number. """
        
    return [int(byte_str)]
    
# WARNING: These aren't "official" data types, and for lack of reference
# similar numbered as IFD data types.
TYPES = {
  1: datatypes.Byte,
  2: datatypes.Ascii,
  3: datatypes.Short,
  4: datatypes.Long,
  5: datatypes.Rational,
  7: datatypes.Undefined,
  15: Digits
} 
