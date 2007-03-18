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
import types

""" This module contains classes for handling the 12 different data types in
    TIFF/Exif data. Each class provides an encode method and a decode method, to
    respectively encode a stream of data into a byte stream, or convert a byte
    stream into a data stream. 
    The TYPES dict matches each data type number to the proper class. """
    
class DataType:
  """ The base class for each data type. Derived classes should set the folowing
      parameters:
      - num:          the data type number according to the Exif/TIFF specs
      - word_width:   the number of bytes in a word
      - is_signed:    whether the number is signed (None if not applicable)
      - word_encoder: a method to encode a single word
      - word_decoder: a method to decode a single word
  """
 
  @classmethod
  def encode(cls, stream, is_big_endian = True):
    # We need to return a string of enoded characters
    encoded_str = ""
    
    # If we got a single number as stream, encapsulate it in a list
    if (type(stream) in [types.IntType, types.LongType, types.FloatType]):
      stream = [stream]
    
    # Encode each number in the stream and append it to the buffer
    for word in stream:
      if (cls.signed != None):
        # If we don't deal with possible signed numbers, don't pass that
        # parameter as well
        encoded_word = cls.word_encoder(word, cls.word_width, cls.signed, is_big_endian)
      else:
        encoded_word = cls.word_encoder(word, cls.word_width, is_big_endian)
        
      encoded_str += encoded_word
      
    return encoded_str
    
  @classmethod
  def decode(cls, byte_str, is_big_endian = True):
    # We need to return a list of decoded numbers
    decoded_nums = []
    
    # Check for the proper number of bytes
    if ((len(byte_str) % cls.word_width) != 0):
      raise "The number of bytes for decoding does not match the specified word width!"
      
    # Iterate over all word_width sized pars and decode them
    for byte_num in range(0, len(byte_str), cls.word_width):
      word = byte_str[byte_num:byte_num + cls.word_width]
      if (cls.signed != None):
        # If we don't deal with possible signed numbers, don't pass that
        # parameter as well
        decoded_word = cls.word_decoder(word, cls.signed, is_big_endian)
      else:
        decoded_word = cls.word_decoder(word, is_big_endian)
        
      decoded_nums.append(decoded_word)
      
    return decoded_nums
  
class Byte(DataType):
  word_width   = 1
  signed       = False
  word_encoder = staticmethod(itob)
  word_decoder = staticmethod(btoi)
  
class Ascii(DataType):
  """ Encoding and decoding ASCII Data is fundamentally different from the
      numerical data types, so we have to do some overriding. """
  word_width = 1
  
  @classmethod
  def encode(cls, stream, is_big_endian = True):
    """ Basically, set the data to the supplied string. The
    is_big_endian parameter is only here for compatibility reasons. """
    
    # We cannot support multiple strings, but we can encode a single string
    # inside a list
    if (type(stream) in [types.TupleType, types.ListType]):
      if (len(stream) > 1):
        raise "Ascii write method does not support encoding multiple strings!"
      else:
        stream = stream[0]
        
    return stream
    
  @classmethod
  def decode(cls, byte_str, is_big_endian = True):
    """ Basically, return the string encoded in a list. The is_big_endian parameter
        is only here for compatibility reasons. """
        
    return [byte_str]
  
class Short(DataType):
  word_width   = 2
  signed       = False
  word_encoder = staticmethod(itob)
  word_decoder = staticmethod(btoi)
  
class Long(DataType):
  word_width   = 4
  signed       = False
  word_encoder = staticmethod(itob)
  word_decoder = staticmethod(btoi)

class Rational(DataType):
  word_width   = 8
  signed       = False
  word_encoder = staticmethod(rtob)
  word_decoder = staticmethod(btor)

class SByte(DataType):
  word_width   = 1
  signed       = True
  word_encoder = staticmethod(itob)
  word_decoder = staticmethod(btoi)
  
class Undefined(DataType):
  """ The Undefined data type lets the user write arbritary bytes to the file.
      This cloes only does some checking. """
      
  word_width = 1
  
  @classmethod
  def encode(cls, byte_stream, is_big_endian = True):
    if (type(byte_stream) != types.StringType):
      raise "You need to encode the data stream yourself for type UNDEFINED!"
      
    return byte_stream
    
  @classmethod
  def decode(cls, byte_stream, is_big_endian = True):
    return byte_stream

class SShort(DataType):
  word_width   = 2
  signed       = True
  word_encoder = staticmethod(itob)
  word_decoder = staticmethod(btoi)
  
class SLong(DataType):
  word_width   = 4
  signed       = True
  word_encoder = staticmethod(itob)
  word_decoder = staticmethod(btoi)
  
class SRational(DataType):
  word_width   = 8
  signed       = True
  word_encoder = staticmethod(rtob)
  word_decoder = staticmethod(btor)
  
class Float(DataType):
  word_width   = 4
  signed       = None
  word_encoder = staticmethod(ftob)
  word_decoder = staticmethod(btof)

class Double(DataType):
  word_width   = 8
  signed       = None
  word_encoder = staticmethod(ftob)
  word_decoder = staticmethod(btof)
  
TYPES = {
  1: Byte,
  2: Ascii,
  3: Short,
  4: Long,
  5: Rational,
  6: SByte,
  7: Undefined,
  8: SShort,
  9: SLong,
  10: SRational,
  11: Float,
  12: Double
} 
