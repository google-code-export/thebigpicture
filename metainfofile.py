class MetaInfoFile:
  """The base class for file containing met information."""
  
  def __init__(self):
    self.ifds = dict.fromkeys(["tiff", "exif", "gps"], None)

  def getTagData(self, tag):
    """ Return the payload of a tag with the specified name. """
    
    payload = None
    
    # Iterate over all IFD's
    for ifd in ['tiff', 'exif', 'gps']:
      if (self.ifds[ifd]):
        payload = self.ifds[ifd].getTagPayload(tag)
        if payload:
          break

    return payload

  def getExifData(self):
    """ Return the encoded Tiff, Exif and GPS IFD's as a block """
    
    # The exif data can have a different endianness than the JPEG file
    ifd_is_be = self.ifds["tiff"].is_be
          
    # Calculate the different byte offsets (within the segment)
    if "exif" in self.ifds:
      exif_ifd_offset = self.ifds["tiff"].getSize() + 8 # 8 for Tiff header
    else:
      exif_ifd_offset = 0
      
    if "gps" in self.ifds:
      gps_ifd_offset  = exif_ifd_offset + self.ifds["exif"].getSize()
    else:
      gps_ifd_offset = 0

    # Set the offsets to the tiff data
    if (exif_ifd_offset):
      self.ifds["tiff"].setTagPayload("Exif IFD Pointer", exif_ifd_offset)
    if (gps_ifd_offset):
      self.ifds["tiff"].setTagPayload("GPSInfo IFD Pointer", gps_ifd_offset)
          
    # Write the Exif IFD's
    byte_str = self.ifds["tiff"].getByteStream(8)
    if ("exif" in self.ifds):
      byte_str += self.ifds["exif"].getByteStream(exif_ifd_offset)
    if ("gps" in self.ifds):
      byte_str += self.ifds["gps"].getByteStream(gps_ifd_offset)
      
    return byte_str
