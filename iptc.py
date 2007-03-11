#from helper import convBytes2Int, convBytes2Float
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
