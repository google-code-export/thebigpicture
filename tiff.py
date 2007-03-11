# Import local classes
import ifd, exif, iptc, metainfofile
from helper import convBytes2Int, convInt2Bytes

# Import python modules
import types

class Tiff(metainfofile.MetaInfoFile):
  def __init__(self, file_indicator, offset = 0):
    """Initialize a Tiff file object. It needs an open file object or a path to
    a file on the disk. A byte offset may be given to the start of the Tiff
    header."""
    
    metainfofile.MetaInfoFile.__init__(self)
    
    # Initialize the file pointer
    if (type(file_indicator) == types.StringType):
      self.fp = file(file_indicator)
    elif (type(file_indicator) == types.FileType):
      self.fp = file_indicator
    else:
      raise "No valid file parameter given -- file path or file object needed." 
      
    # Parse the header
    self.parseFile(offset)
      
  def parseFile(self, offset):
    """Parse the header of the Tiff file, starting ot the byte offset.""" 
    is_tiff = False
    self.fp.seek(offset)
    
    # Read the header
    data = self.fp.read(2)
    if (data == "MM"):
      self.is_be = True
      is_tiff = True
    elif (data == "II"):
      self.is_be = False
      is_tiff = True
      
    # The next two bytes should be 42
    if (is_tiff) and (convBytes2Int(self.fp.read(2), self.is_be) == 42):
      is_tiff = True
      
    # If the file does not have a Tiff header, report it as false 
    if not(is_tiff):
      raise "File is not Tiff"
    
    # Map all the IFD's
    
    # Get the first IFD (The "Tiff" tags)
    ifd_offsets = {}
    ifd_offsets["tiff"] = convBytes2Int(self.fp.read(4), self.is_be)
    self.ifds["tiff"] = exif.TIFF(self.fp, ifd_offsets["tiff"], offset, self.is_be)
    
    # Get the Exif tags
    ifd_offsets["exif"] = self.ifds["tiff"].getPayload("Exif IFD Pointer")
    if (ifd_offsets["exif"]):
      self.ifds["exif"] = exif.Exif(self.fp, ifd_offsets["exif"], offset, self.is_be)
      
    # Get the GPS tags
    ifd_offsets["gps"] = self.ifds["tiff"].getPayload("GPSInfo IFD Pointer")
    if (ifd_offsets["gps"]):
      self.ifds["gps"] = exif.GPS(self.fp, ifd_offsets["gps"], offset, self.is_be)

    # Get the IPTC block. The payload isn't the position in the file, but
    # rather the IPTC content. To let the IPTC class do its job, we feed it
    # the position of the block.
    if (33723 in self.ifds["tiff"].disk_fields):
      iptc_offset = self.ifds["tiff"].disk_fields[33723][0]
      iptc_length = self.ifds["tiff"].disk_fields[33723][2]
      self.iptc_info = iptc.IPTC(self.fp, iptc_offset, iptc_length) 
    else:
      self.iptc_info = None
      
    #self.fp.seek(self.ifd_offsets["ifd0"] + self.ifds["ifd0"].getSize())
    #data = convBytes2Int(self.fp.read(4))
    #if (data != 0):
    #  self.ifd_offsets["ifd1"] = data
    #  self.ifds["ifd1"] = ifd.IFD(self.fp, self.ifd_offsets["ifd1"], self.is_be)
    
  def writeFile(self, file_path):
    out_fp = file(file_path, "w")
    if (self.is_be):
      out_fp.write("\x4d\x4d")
    else:
      out_fp.write("\x49\x49")
    out_fp.write(convInt2Bytes(42, 2, self.is_be))
    out_fp.write(convInt2Bytes(8, 4, self.is_be))
    entry_stream, data_stream = self.ifds["tiff"].getByteStream(12) # 8 bytes header + 4 bytes at end of entry stream
    out_fp.write(entry_stream)
    out_fp.write(convInt2Bytes(0, 4, self.is_be))
    out_fp.write(data_stream)
    out_fp.close()
