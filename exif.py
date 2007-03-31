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

import metainfofile, ifd, qdb, ifddatatypes

# The Tiff IFD (first part off IFD0 in Tiff file).
class TiffIFD(ifd.IFD):
  tags = qdb.QDB()
  # This info is taken from the Exif 2.2 specification, page 54
  tags.addList("name",      ["ImageWidth", "ImageLength", "BitsPerSample", "Compression", "PhotometricInterpretation", "ImageDescription", "Make", "Model", "StripOffsets", "Orientation", "SamplesPerPixel", "RowsPerStrip", "StripByteCounts", "XResolution", "YResolution", "PlanarConfiguration", "ResolutionUnit", "TransferFunction", "Software", "DateTime", "Artist", "WhitePoint", "PrimaryChromaticities", "JPEGInterchangeFormat", "JPEGInterchangeFormatLength", "YCbCrCoefficients", "YCbCrSubSampling", "YCbCrPositioning", "ReferenceBlackWhite", "IPTC-NAA", "Copyright", "Exif IFD Pointer", "GPSInfo IFD Pointer"])
  tags.addList("num",       [256, 257, 258, 259, 262, 270, 271, 272, 273, 274, 277, 278, 279, 282, 283, 284, 296, 301, 305, 306, 315, 318, 319, 513, 514, 529, 530, 531, 532, 33723, 33432, 34665, 34853])
  tags.addList("data_type", [[3, 4], [3, 4], 3, 3, 3, 2, 2, 2, [3, 4], 3, 3, [3, 4], [3, 4], 5, 5, 3, 3, 3, 2, 2, 2, 5, 5, 4, 4, 5, 3, 3, 5, 7, 2, 4, 4])
  # -1 means special, None means any
  tags.addList("count",     [1, 1, 3, 1, 1, None, None, None, -1, 1, 1, 1, -1, 1, 1, 1, 1, -1, None, 20, None, 2, 6, 1, 1, 3, 2, 1, 6, 1, None, 1, 1])
  #  required = [256, 257, 258, 259, 262, 273, 277, 278, 279, 282, 283, 296, 34665]

class ExifIFD(ifd.IFD):
  # The Exif data.
  tags = qdb.QDB()
  # This info is taken from the Exif 2.2 specification, page 24 and 25 (with the
  # exception of the Interoperability IFD Pointer
  tags.addList("name",      ["ExposureTime", "FNumber", "ExposureProgram", "SpectralSensitivity", "ISOSpeedRatings", "OECF", "ExifVersion", "DateTimeOriginal", "DateTimeDigitized", "ComponentsConfiguration", "CompressedBitsPerPixel", "ShutterSpeedValue", "ApertureValue", "BrightnessValue", "ExposureBiasValue", "MaxApertureValue", "SubjectDistance", "MeteringMode", "LightSource", "Flash", "FocalLength", "SubjectArea", "MakerNote", "UserComment", "SubSecTime", "SubSecTimeOriginal", "SubSecTimeDigitized", "FlashpixVersion", "ColorSpace", "PixelXDimension", "PixelYDimension", "RelatedSoundFile", "Interoperability IFD Pointer", "FlashEnergy", "SpatialFrequencyResponse", "FocalPlaneXResolution", "FocalPlaneYResolution", "FocalPlaneResolutionUnit", "SubjectLocation", "ExposureIndex", "SensingMethod", "FileSource", "SceneType", "CFAPattern", "CustomRendered", "ExposureMode", "WhiteBalance", "DigitalZoomRatio", "FocalLengthIn35mmFilm", "SceneCaptureType", "GainControl", "Contrast", "Saturation", "Sharpness", "DeviceSettingDescription", "SubjectDistanceRange", "ImageUniqueID"])
  tags.addList("num",       [33434, 33437, 34850, 34852, 34855, 34856, 36864, 36867, 36868, 37121, 37122, 37377, 37378, 37379, 37380, 37381, 37382, 37383, 37384, 37385, 37386, 37396, 37500, 37510, 37520, 37521, 37522, 40960, 40961, 40962, 40963, 40964, 40965, 41483, 41484, 41486, 41487, 41488, 41492, 41493, 41495, 41728, 41729, 41730, 41985, 41986, 41987, 41988, 41989, 41990, 41991, 41992, 41993, 41994, 41995, 41996, 42016])
  tags.addList("data_type", [5, 5, 3, 2, 3, 7, 7, 2, 2, 7, 5, 10, 5, 10, 10, 5, 5, 3, 3, 3, 5, 3, 7, 7, 2, 2, 2, 7, 3, [3, 4], 3 or 4, 2, 4, 5, 7, 5, 5, 3, 3, 5, 3, 7, 7, 7, 3, 3, 3, 5, 3, 3, 5, 3, 3, 3, 7, 3, 2])
  tags.addList("count",     [1, 1, 1, None, None, None, 4, 20, 20, 4, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, -1, None, None, None, None, None, 4, 1, 1, 1, 13, 1, 1, None, 1, 1, 1, 2, 1, 1, 1, 1, None, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, None, 1, 33])

class GPSIFD(ifd.IFD):
  # The GPS data.
  tags = qdb.QDB()
  # This info is taken from the Exif 2.2 specification, page 46
  tags.addList("name",      ["GPSVersionID", "GPSLatitudeRef", "GPSLatitude", "GPSLongitudeRef", "GPSLongitude", "GPSAltitudeRef", "GPSAltitude", "GPSTimeStamp", "GPSSatellites", "GPSStatus", "GPSMeasureMode", "GPSDOP", "GPSSpeedRef", "GPSSpeed", "GPSTrackRef", "GPSTrack", "GPSImgDirectionRef", "GPSImgDirection", "GPSMapDatum", "GPSDestLatitudeRef", "GPSDestLatitude", "GPSDestLongitudeRef", "GPSDestLongitude", "GPSDestBearingRef", "GPSDestBearing", "GPSDestDistanceRef", "GPSDestDistance", "GPSProcessingMethod", "GPSAreaInformation", "GPSDateStamp", "GPSDifferential"])
  tags.addList("num",       [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30])
  tags.addList("data_type", [1, 2, 5, 2, 5, 1, 5, 5, 2, 2, 2, 5, 2, 5, 2, 5, 2, 5, 2, 2, 5, 2, 5, 2, 5, 2, 5, 7, 7, 2, 3])
  tags.addList("count",     [4, 2, 3, 2, 3, 1, 1, 3, None, 2, 2, 1, 2, 1, 2, 1, 2, 1, None, 2, 3, 2, 3, 2, 1, 2, 1, None, None, 11, 1])
  #  required  = []

class InteropIFD(ifd.IFD):
  tags = qdb.QDB()
  tags.addList("name", [])
  tags.addList("num", [])
  tags.addList("data_type", [])
  tags.addList("count", [])

class Exif(metainfofile.MetaInfoBlock):    
  def __init__(self, file_pointer, ifd_offset, header_offset = 0, big_endian = True):
    """ Read and write an Exif segment in a file. TODO: loading from memory. """
    
    self.big_endian = big_endian
    
    # Try to parse the tiff data, and balk if it isn't there
    tiff = TiffIFD(file_pointer, ifd_offset, header_offset, big_endian = big_endian)
    if not (tiff.hasTags()):
      raise "No valid Exif data found!"

    # Create the IFD objects for the other relevant IFD's
    exif_offset = tiff.getTag(34665)
    if (exif_offset):
      exif = ExifIFD(file_pointer, exif_offset, header_offset, big_endian = big_endian)
    else:
      exif = ExifIFD()
      
    gps_offset = tiff.getTag(34853)
    if (gps_offset):
      gps = GPSIFD(file_pointer, gps_offset, header_offset, big_endian = big_endian)
    else:
      gps = GPSIFD()

    interop_offset = exif.getTag(40965)
    if (interop_offset):
      interop = InteropIFD(file_pointer, interop_offset, header_offset, big_endian = big_endian)
    else:
      interop = InteropIFD()
    
    # Create the database of segment data
    self.records = qdb.QDB()
    self.records.addList("num", [1, 2, 3, 4])
    self.records.addList("name", ["tiff", "exif", "gps", "interop"])
    self.records.addList("record", [tiff, exif, gps, interop])
    
  def getSize(self):
    """ Return the total size of the encoded Exif blocks. """
    
    size = 0
    
    # Query each record for the size
    for record in self.records.getList("record"):
      if (record.hasTags()):
        size += record.getSize()
      
    return size
    
  def getBlob(self, offset = 0):
    """ Return the encoded Tiff, Exif, GPS, and Interoperability IFD's as a
        block. The offset specifies the offset that needs to be added to all
        data offsets (usually this will be 8 bytes for the Tiff header). """
    
    # Retrieve the necessary IFD's
    tiff    = self.records.query("name", "tiff", "record")
    exif    = self.records.query("name", "exif", "record")
    gps     = self.records.query("name", "gps", "record")
    interop = self.records.query("name", "interop", "record")
    
    # Decide whether the tags pointing to other IFD's should be present. As we
    # don't know the offsets yet, we simply set them to zero. This procedure is
    # needed so we can calcuate the proper size of each IFD (and hence, the
    # offsets).
    
    # Interopability IFD needs to go first, since it is stored in the Exif IFD,
    # which may be empty or not depending on the prescence of the Interop IFD.
    if (interop.hasTags()):
      exif.setTag(40965, 0)
    else:
      exif.removeTag(40965)
      
    # Exif IFD
    if (exif.hasTags()):
      tiff.setTag(34665, 0)
    else:
      tiff.removeTag(34665)
    
    # GPS IFD
    if (gps.hasTags()):
      tiff.setTag(34853, 0) # Offset to GPS IFD
    else:
      tiff.removeTag(34853)

    # Now that we can determine the size of each IFD, determine their offsets
    # and store them in the appropriate tags.
    curr_offset = offset + tiff.getSize()
    if (exif.hasTags()):
      exif_offset = curr_offset
      tiff.setTag(34665, exif_offset)
      curr_offset += exif.getSize()
    if (gps.hasTags()):
      gps_offset = curr_offset
      tiff.setTag(34853, gps_offset)
      curr_offset += gps.getSize()
    if (interop.hasTags()):
      interop_offset = curr_offset
      exif.setTag(40965, interop_offset)
      
    # Write the Exif IFD's
    byte_str = tiff.getBlob(offset)
    if (exif.hasTags()):
      byte_str += exif.getBlob(exif_offset)
    if (gps.hasTags()):
      byte_str += gps.getBlob(gps_offset)
    if (interop.hasTags()):
      byte_str += interop.getBlob(interop_offset)
      
    return byte_str
