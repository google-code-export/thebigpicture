import ifd

class TIFFData(ifd.IFD):
  """The Tiff IFD (first part off IFD0 in Tiff file)."""

  # This info is taken from the Exif 2.2 specification, page 54
  tag_names = ["ImageWidth", "ImageLength", "BitsPerSample", "Compression", "PhotometricInterpretation", "ImageDescription", "Make", "Model", "StripOffsets", "Orientation", "SamplesPerPixel", "RowsPerStrip", "StripByteCounts", "XResolution", "YResolution", "PlanarConfiguration", "ResolutionUnit", "TransferFunction", "Software", "DateTime", "Artist", "WhitePoint", "PrimaryChromaticities", "JPEGInterchangeFormat", "JPEGInterchangeFormatLength", "YCbCrCoefficients", "YCbCrSubSampling", "YCbCrPositioning", "ReferenceBlackWhite", "Copyright", "Exif IFD Pointer", "GPSInfo IFD Pointer"]
  
  tag_nums = [256, 257, 258, 259, 262, 270, 271, 272, 273, 274, 277, 278, 279, 282, 283, 284, 296, 301, 305, 306, 315, 318, 319, 513, 514, 529, 530, 531, 532, 33432, 34665, 34853]
  
  required_tags = [256, 257, 258, 259, 262, 273, 277, 278, 279, 282, 283, 296, 34665]
  
class Exif(ifd.IFD):
  """The Exif data."""
  
  # This info is taken from the Exif 2.2 specification, page 54
  tag_names = ["ExposureTime", "FNumber", "ExposureProgram", "SpectralSensitivity", "ISOSpeedRatings", "OECF", "ExifVersion", "DateTimeOriginal", "DateTimeDigitized", "ComponentsConfiguration", "CompressedBitsPerPixel", "ShutterSpeedValue", "ApertureValue", "BrightnessValue", "ExposureBiasValue", "MaxApertureValue", "SubjectDistance", "MeteringMode", "LightSource", "Flash", "FocalLength", "SubjectArea", "MakerNote", "UserComment", "SubSecTime", "SubSecTimeOriginal", "SubSecTimeDigitized", "FlashpixVersion", "ColorSpace", "PixelXDimension", "PixelYDimension", "RelatedSoundFile", "Interoperability IFD Pointer", "FlashEnergy", "SpatialFrequencyResponse", "FocalPlaneXResolution", "FocalPlaneYResolution", "FocalPlaneResolutionUnit", "SubjectLocation", "ExposureIndex", "SensingMethod", "FileSource", "SceneType", "CFAPattern", "CustomRendered", "ExposureMode", "WhiteBalance", "DigitalZoomRatio", "FocalLengthIn35mmFilm", "SceneCaptureType", "GainControl", "Contrast", "Saturation", "Sharpness", "DeviceSettingDescription", "SubjectDistanceRange", "ImageUniqueID"]

  tag_nums = [33434, 33437, 34850, 34852, 34855, 34856, 36864, 36867, 36868, 37121, 37122, 37377, 37378, 37379, 37380, 37381, 37382, 37383, 37384, 37385, 37386, 37396, 37500, 37510, 37520, 37521, 37522, 40960, 40961, 40962, 40963, 40964, 40965, 41483, 41484, 41486, 41487, 41488, 41492, 41493, 41495, 41728, 41729, 41730, 41985, 41986, 41987, 41988, 41989, 41990, 41991, 41992, 41993, 41994, 41995, 41996, 42016]
  
  required_tags = [36864, 40960, 40961]

class GPS(ifd.IFD):
  """The GPS data."""

  # This info is taken from the Exif 2.2 specification, page 55
  tag_names = ["GPSVersionID", "GPSLatitudeRef", "GPSLatitude", "GPSLongitudeRef", "GPSLongitude", "GPSAltitudeRef", "GPSAltitude", "GPSTimeStamp", "GPSSatellites", "GPSStatus", "GPSMeasureMode", "GPSDOP", "GPSSpeedRef", "GPSSpeed", "GPSTrackRef", "GPSTrack", "GPSImgDirectionRef", "GPSImgDirection", "GPSMapDatum", "GPSDestLatitudeRef", "GPSDestLatitude", "GPSDestLongitudeRef", "GPSDestLongitude", "GPSDestBearingRef", "GPSDestBearing", "GPSDestDistanceRef", "GPSDestDistance", "GPSProcessingMethod", "GPSAreaInformation", "GPSDateStamp", "GPSDifferential"]
  
  tag_nums = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30]
  
  required_tags = []
