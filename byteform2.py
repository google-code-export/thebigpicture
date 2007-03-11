import struct

BYTE      = 1
ASCII     = 2
SHORT     = 3
LONG      = 4
RATIONAL  = 5
SBYTE     = 6
UNDEFINED = 7
SSHORT    = 8
SLONG     = 9
SRATIONAL = 10
FLOAT     = 11
DOUBLE    = 12

def pack(format, is_big_endian, data):
  format_str = __getFormatChars(format, is_big_endian)
  return struct.pack(format_str, *data)
  
def unpack(format_str, is_big_endian, byte_str):
  format_str = __getFormatChars(format, is_big_endian)
  return struct.unpack(format_str, byte_str)
  
def __getFormatChars(format, is_big_endian):
  if (is_big_endian):
    format_str = ">" + format_str
  else:
    format_str = "<" + format_str

  for data_type in format:
    if (data_type == BYTE):
      format += "B"
    elif (data_type == ASCII):
      format += ""  
    elif (data_type == SHORT):
      format += "H"  
    elif (data_type == LONG):
      format += "L"  
    elif (data_type == RATIONAL):
      format += ""  
    elif (data_type == SBYTE):
      format += "b"  
    elif (data_type == UNDEFINED):
      format += ""  
    elif (data_type == SSHORT):
      format += "h"  
    elif (data_type == SLONG):
      format += "l"  
    elif (data_type == SRATIONAL):
      format += ""  
    elif (data_type == FLOAT):
      format += "f"  
    elif (data_type == DOUBLE):
      format += "d"
      
  return format
   
