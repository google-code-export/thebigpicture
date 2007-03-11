from byteform import *
import types

""" This module contains classes for handling the 12 different data types in
    TIFF/Exif data. Each class provides an encode method and a decode method, to
    respectively encode a stream of data into a byte stream, or convert a byte
    stream into a data stream. 
    The DATA_TYPES dict matches each data type number to the proper class. """
    
class DataType:
  """ The base class for each data type. Derived classes should set the folowing
      parameters:
      - word_width:   the number of bytes in a word
      - is_signed:    whether the number is signed (None if not applicable)
      - word_encoder: a method to encode a single word
      - word_decoder: a method to decode a single word
  """
   
  def encode(self, stream, is_big_endian = True):
    encoded_str = ""
    for word in stream:
      if (self.is_signed != None):
        encoded_word = self.word_encoder(word, self.word_width, self.signed, is_big_endian)
      else:
        encoded_word = self.word_encoder(word, self.word_width, is_big_endian)
        
      encoded_str += encoded_word
      
    return encoded_str
    
  def decode(self, byte_str, is_big_endian):
    decoded_nums = []
    for byte_num in range(0, len(byte_str), self.word_width):
      decoded_nums.append(self.word_deocder(byte_str[byte_num:byte_num + self.word_width], self.signed, is_big_endian))
      
    return decoded_stream
  
class Byte(DataType):
  word_width = 1
  signed     = False
  
class Ascii:
  def encode(self, streams, is_big_endian):
    if (type(streams) == types.StringType):
      streams = [streams]
      
    byte_stream = ""
    for stream in streams:
      byte_stream += stream + "\x00"
      
    return byte_stream
    
  def decode(self, byte_stream, is_big_endian):
    streams = []
    stream_num = 0
    for char in byte_stream:
      if (char == "\x00"):
        stream_num += 1
        streams.append("")
      else:
        streams[stream_num] += char
        
    return streams
  
class Short(DataType):
  word_width = 2
  signed     = False
  
class Long(DataType):
  word_width = 4
  signed     = False

class Rational:
  word_width = 8
  signed     = False
  
  def encode(self, stream, is_big_endian):
    encoded_str = ""
    for word in stream:
      encoded_str += rtob(word, self.word_width, self.signed, is_big_endian)
      
    return encoded_str
    
  def decode(self, byte_stream, is_big_endian):
    decoded_nums = []
    for byte_num in range(0, len(byte_str), self.word_width):
      decoded_nums.append(btor(byte_str[byte_num:byte_num + self.word_width], self.signed, is_big_endian))
      
    return decoded_stream

class SByte(DataType):
  word_width = 1
  signed     = True
  
class Undefined:
  word_width = 1
  
  def encode(self, byte_stream, is_big_endian):
    if (type(byte_stream) != types.StringType):
      raise "You need to encode the data stream yourself for type UNDEFINED!"
      
    return byte_stream
    
  def decode(self, byte_stream, is_big_endian):
    return byte_stream

class SShort(DataType):
  word_width = 2
  signed     = True
  
class SLong(DataType):
  word_width = 4
  signed     = True
  
class SRational(Rational):
  signed = True
  
class Float:
  word_width = 4

  def encode(self, stream, is_big_endian = True):
    encoded_stream = ""
    for char in stream:
      encoded_stream += ftob(char, self.word_width, is_big_endian, True)
      
    return encoded_stream
    
  def decode(self, byte_stream, is_big_endian):
    decoded_nums = []
    for byte_num in range(0, len(byte_stream), self.word_width):
      decoded_nums.append(btof(byte_stream[byte_num:byte_num + self.word_width], is_big_endian))
      
    return decoded_nums

class Double(Float):
  word_width = 8
  
DATA_TYPES = {1: Byte, 2: Ascii, 3: Short, 4: Long, 5: Rational, 6: SByte, 7: Undefined, 8: SShort, 9: SLong, 10: SRational, 11: Float, 12: Double} 
