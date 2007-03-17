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
  
class Ascii(datatypes.DataType):
  """ In exif, strings are capped with a zero byte, and abyte stream may contain
      multiple strings. """
  word_width = 1
  
  @classmethod
  def encode(cls, streams, is_big_endian = True):
    """ Encode either a string or a list of strings to ASCII data. The
    is_big_endian parameter is only here for compatibility reasons. """
    
    # If the user passed a string, put it in a list for easier handling
    if (type(streams) == types.StringType):
      streams = [streams]
      
    # Iterate over the strings and put a null character at each end
    byte_stream = ""
    for stream in streams:
      byte_stream += stream + "\x00"
      
    return byte_stream
    
  @classmethod
  def decode(cls, byte_stream, is_big_endian = True):
    """ Convert a byte stream to a list of strings. The is_big_endian parameter
        is only here for compatibility reasons. """
        
    streams = []
    
    # Iterate over all the characters in the byte stream, and start a new string
    # at every null character
    for char in byte_stream:
      if (char == "\x00"):
        streams.append("")
      else:
        streams[-1] += char
        
    return streams
    
TYPES = {
  1: datatypes.Byte,
  2: Ascii,
  3: datatypes.Short,
  4: datatypes.Long,
  5: datatypes.Rational,
  6: datatypes.SByte,
  7: datatypes.Undefined,
  8: datatypes.SShort,
  9: datatypes.SLong,
  10: datatypes.SRational,
  11: datatypes.Float,
  12: datatypes.Double
} 
