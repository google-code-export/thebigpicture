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

def convBytes2Int(bytes, big_endian = True, signed = False):
  """Converts a string of bytes to a number, according to its endianness (True
  means big endian (Motorola), False means little endian (Intel))."""
  
  num = 0

  for byte_num in range(len(bytes)):
    if (big_endian):
      sq = len(bytes) - byte_num - 1
    else:
      sq = byte_num
      
    num += ord(bytes[byte_num]) * (256 ** sq)
    
  if (signed):
    if (big_endian):
      msb = bytes[0]
    else:
      msb = bytes[1]
    if ((ord(msb) >> 7) == 1):
      num -= (256 ** len(bytes))

  return num

def convInt2Bytes(num, num_bytes, big_endian = True, signed = False):
  """Converts a integer number to a string of bytes to a number, according to
  its endianness (True means big endian (Motorola), False means little endian (Intel)). You can specify how many bytes it needs to occupy with num_bytes."""
  
  # Calculate the needed byte positions
  required_bytes = 1
  while True:
    if ((num >> (required_bytes * 8)) in [0, -1]):
      break
    required_bytes += 1

  # Compensate for signed numbers
  if (signed):
    if (num > (((256 ** required_bytes) - 1) / 2)):
      required_bytes += 1
    elif (num < (-1 * ((256 ** required_bytes) / 2))):
      required_bytes += 1
    
    if (num < 0):
      num += (256 ** required_bytes)
      
  if (required_bytes > num_bytes):
    raise "Number doesn't fit in the avaiable word length!"
    
  # Calculate the byte stream    
  bytes = []
  for byte_num in range(1, num_bytes + 1):
    bytes.append(chr(num % (256 ** byte_num)))
    num = num >> (byte_num * 8)

  # Reverse the stream if we're big endian    
  if (big_endian):
    bytes.reverse()
    
  # Convert to string and return
  bytes = ''.join(bytes)    
  return bytes
  
def convBytes2Float(bytes, big_endian = True):
  """Converts a string of bytes to a single (4 bytes) or double (8 bytes) IEEE
  float."""
  
  # Some numbers can be denormal (if exponent is zero)
  is_denormal = False
  
  if (len(bytes) == 4):
    is_single = True
  else:
    is_single = False
  
  if not (big_endian):
    bytes = bytes[::-1] # Invert bytes string

  # The first bit tells us if the number is positive or negative
  byte = ord(bytes[0])
  bytes = bytes[1:]
  if ((byte & 128) == 128):
    sign = -1
  else:
    sign = 1

  # The reamineder of the byte forms the first part of the exponent
  exponent = byte & 127 # byte & 01111111
  
  # The rest of the exponent is formed by 1 (single precision) or 4 (double
  # precision) bits of the next byte
  byte = ord(bytes[0])
  bytes = bytes[1:]
  if (is_single):
    exponent <<= 1
    exponent |= (byte & 128) >> 7 # byte & 10000000, shifted to far right
    exponent -= 127
    if (exponent == -127):
      is_denormal = True
  else:
    exponent <<= 4
    exponent |= (byte & 240) >> 4 # byte & 11110000, shifted to far right
    exponent -= 1023
    if (exponent == -1023):
      is_denormal = True
  if (is_denormal):
    exponent += 1

  # The mantissa is the fraction after the 1, or after the 0 if the exponent is
  # all zeroes. It is representated by the rest of the byte plus the remainder
  # of bytes
  if (is_single):
    mantissa = (byte & 127) # byte & 01111111
  else:
    mantissa = (byte & 15) # byte & 00001111
  
  for byte in bytes:
    mantissa = mantissa << 8
    mantissa = mantissa | ord(byte)
  
  if (is_denormal):
    mantissa_base = 0.0
  else:
    mantissa_base = 1.0

  print sign, mantissa, exponent
  # Put it all together
  if (is_single):
    mantissa = mantissa_base + (mantissa / 8388608.)
  else:
    mantissa = mantissa_base + (mantissa / 4503599627370496.)

  # FIXME: For too small numbers, 0.0 is returned
  # FIXME: Negative zeroes, NaN and infinity are not produced
  return sign * mantissa * (2**exponent)

def convFloat2Bytes(num, double = False, big_endian = True):
  """ Convert a single or double precision IEEE floating point number to its
      byte representation. If double is True, a double precision (8 byte) value
      is returned, otherwise a single precision (4 byte) number. """
