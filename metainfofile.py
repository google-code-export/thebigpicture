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
        payload = self.ifds[ifd].getPayload(tag)
        if payload:
          break

    return payload

