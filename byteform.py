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

""" This module converts data to their byte-representation and vice versa. """

import struct
# The conversions are mostly based on the struct module, which converts to and
# from C structs. The actual outcome is partly based on the machine type, so we
# need to abstract this a bit.

# A small problem arises because in Python < 2.5, no checking is done on the
# number range when byte order and alignment are specified. So we need to do
# this ourselves. These tables specify the lower and upper bounds for both
# unsigned (False) and signed (True) integer numbers.
# For floating point numbers, this is not needed, since otherwise 0 or infinity
# are assumed.
min_int_values = {
  False: {1: 0, 2: 0, 4: 0},
  True:  {1: -128, 2: -32768, 4: -2147483648}
}
max_int_values = {
  False: {1: 255,  2: 65535,  4: 4294967295},
  True:  {1: 127,  2: 32767,  4: 2147483647}
}

def itob(num, num_bytes, signed = False, big_endian = True):
  """ Converts an integer number to its binary representation, with the
      required number of bytes (1, 2 or 4). """
  
  if (num < min_int_values[signed][num_bytes]) or (num > max_int_values[signed][num_bytes]):
    raise "The integer number falls outside the range for encoding!"
    
  control_chars = __getIntControlChars__(num_bytes, signed, big_endian)
  return struct.pack(control_chars, num)
  
def btousi(bytes, big_endian = True):
  """ Convert a string of bytes to an unsigned integer. This function is
      more efficient than btoi, but applicable to a smaller number of cases. """

  num = 0
  if (big_endian):
    step = 1
  else:
    step = -1
  for byte in bytes[::step]:
    num = (num << 8) | ord(byte)
  return num

def btoi(bytes, signed = False, big_endian = True):
  """ Convers a string of bytes to its integer number. The string should
      contain either 1, 2 or 4 bytes. """
  
  control_chars = __getIntControlChars__(len(bytes), signed, big_endian)
  return struct.unpack(control_chars, bytes)[0]

def ftob(num, num_bytes, big_endian = True):
  """ Converts a floating point number to its IEEE representation. """
  
  control_chars = __getFloatControlChars(num_bytes, big_endian)
  return struct.pack(control_chars, num)
  
def btof(bytes, big_endian = True):
  """ Converts a byte stream to a floating point IEEE representation. """
  
  control_chars = __getFloatControlChars(len(bytes), big_endian)
  return struct.unpack(control_chars, bytes)
  
def rtob(num, num_bytes, signed = False, big_endian = True):
  """ Converts a floating point number to a rational byte representation. 
      num_bytes specifies how many bytes the total representation takes, so each
      part of the rational gets half that many bytes. """
      
  # We take a lazy approach, by making the denominator only a power of ten

  num_bytes /= 2
  
  # If we should encode 0, fraction should be 0, denominator should be 1
  if (num == 0.0):
    frac  = 0
    denom = 1
  else:
    # First, find out the multiplier and denominator to get a fraction between 1
    # and 10, or stop when it gets too large. In this case, the number is too
    # small and we simply set it to 0.
    max_num    = max_int_values[signed][num_bytes]
    too_small  = False
    multiplier = 1.0
    while (abs(num * multiplier) < 1):
      multiplier *= 10
      if ((multiplier * num) > max_num):
        multiplier /= 10
        too_small = True
        break
  
    # Then, search for a multiplier where dividing the fraction on the denominator
    # produces the number, or stop when it gets too large
    while (float(long(num * multiplier) / multiplier) != num) and ((multiplier * num)> (max_num / 10)):
      multiplier *= 10
      
    # Calculate the fraction, and set the denominator to the multiplier 
    if (too_small):
      frac  = 0
      denom = 1
    else:
      frac  = int(num * multiplier)
      denom = int(multiplier)
    
  # Create the byte stream
  byte_str =  itob(frac, num_bytes, signed, big_endian)
  byte_str += itob(denom, num_bytes, signed, big_endian)
  return byte_str
  
def btor(byte_str, signed = False, big_endian = True):
  """ Convert a byte stream to a rational number. """
  
  # Check for the proper number of bytes
  if (len(byte_str) != 8):
    raise "A rational number should contain exactly 8 bytes."
  
  # Get the fraction and denominator
  frac  = float(btoi(byte_str[:4], signed, big_endian))
  denom = float(btoi(byte_str[4:], signed, big_endian))
  
  return frac / denom
  
def __getIntControlChars__(length, signed, big_endian = True):
  """ Chooses the format character for struct.(un)pack for integer numbers. """
  
  # Choose the format letter
  if (length == 1):
    format = "b" # Char
  elif (length == 2):
    format = "h" # Short
  elif (length == 4):
    format = "l" # Long
  else:
    raise "You need either 1, 2, or 4 bytes for an integer number."

  # Modify the format letter to either signed or unsigned
  if (not signed):
    format = format.upper()
  
  # Put the proper byte order and alignment character in front 
  format = __getByteAlignmentChar(big_endian) + format
  
  return format
  
def __getFloatControlChars(length, big_endian):
  """ Chooses the format character for struct.(un)pack for floating point
      numbers. """
      
  # Choose the format letter
  if (length == 4):
    format = "f" # Float
  elif (length == 8):
    format = "d" # Double
  else:
    raise "You need either 4 or 8 bytes for a float."
  
  # Put the proper byte order and alignment character in front 
  format = __getByteAlignmentChar(big_endian) + format
  
  return format

def __getByteAlignmentChar(big_endian):
  """ Choose the control character at the start of the byte string, for
      representing byte order and alignment. """
      
  if (big_endian):
    format = ">"
  else:
    format = "<"
    
  return format

