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

import byteform, iptc, datablock, metainfofile, qdb

class IPTCEnvelope(iptc.IPTCRecord):
  RECORD_NUM = 1
  tags = qdb.QDB()
  tags.addList("name", ["EnvelopeRecordVersion", "Destination", "FileFormat", "FileVersion", "ServiceIdentifier", "EnvelopeNumber", "ProductID", "EnvelopePriority", "DateSent", "TimeSent", "CodedCharacterSet", "UniqueObjectName", "ARMIdentifier", "ARMVersion"])
  tags.addList("num", [0, 5, 20, 22, 30, 40, 50, 60, 70, 80, 90, 100, 120, 122])
  tags.addList("count", [1, 1, 1, 1, [0, 10], 8, [0, 32], 1, 8, 11, [0.32], [14, 80], 1, 1])
  tags.addList("data_type", [3, 2, 3, 3, 2, 15, 2, 15, 15, 2, 2, 2, 3, 3])

class IPTCApplication(iptc.IPTCRecord):
  RECORD_NUM = 2
  tags = qdb.QDB()
  tags.addList("name", ["ApplicationRecordVersion","ObjectTypeReference","ObjectAttributeReference","ObjectName","EditStatus","EditorialUpdate","Urgency","SubjectReference","Category","SupplementalCategories","FixtureIdentifier","Keywords","ContentLocationCode","ContentLocationName","ReleaseDate","ReleaseTime","ExpirationDate","ExpirationTime","SpecialInstructions","ActionAdvised","ReferenceService","ReferenceDate","ReferenceNumber","DateCreated","TimeCreated","DigitalCreationDate","DigitalCreationTime","OriginatingProgram","ProgramVersion","ObjectCycle","By-line","By-lineTitle","City","Sub-location","Province-State","Country-PrimaryLocationCode","Country-PrimaryLocationName","OriginalTransmissionReference","Headline","Credit","Source","CopyrightNotice","Contact","Caption-Abstract","LocalCaption","Writer-Editor","RasterizedCaption","ImageType","ImageOrientation","LanguageIdentifier","AudioType","AudioSamplingRate","AudioSamplingResolution","AudioDuration","AudioOutcue","JobID","MasterDocumentID","ShortDocumentID","UniqueDocumentID","OwnerID","ObjectPreviewFileFormat","ObjectPreviewFileVersion","ObjectPreviewData","ClassifyState","SimilarityIndex","DocumentNotes","DocumentHistory","ExifCameraInfo"])
  tags.addList("num", [0, 3, 4, 5, 7, 8, 10, 12, 15, 20, 22, 25, 26, 27, 30, 35, 37, 38, 40, 42, 45, 47, 50, 55, 60, 62, 63, 65, 70, 75, 80, 85, 90, 92, 95, 100, 101, 103, 105, 110, 115, 116, 118, 120, 121, 122, 125, 130, 131, 135, 150, 151, 152, 153, 154, 184, 185, 186, 187, 188, 200, 201, 202, 225, 228, 230, 231, 232])
  tags.addList("count", [1, [3, 67], [4, 68], [0, 64], [0, 64], 2, 1, [13, 236], [0, 3], [0, 32], [0, 32], [0, 64], 3, [0, 64], 8, 11, 8, 11, [0, 256], 2, [0, 10], 8, 8, 8, 11, 8, 11, [0, 32], [0, 10], 1, [0, 32], [0, 32], [0, 32], [0, 32], [0, 32], 3, [0, 64], [0, 32], [0, 256], [0, 32], [0, 32], [0, 128], [0, 128], [0, 2000], [0, 256], [0, 32], 7360, 2, 1, [2, 3], 2, 6, 2, 6, [0, 64], [0, 64], [0, 256], [0, 64], [0, 128], [0, 128], 0, 1, [0, 256000], [0, 64], [0, 32], [0, 1024], [0, 256], [0, 4096]])
  tags.addList("data_type", [3, 2, 2, 2, 2, 15, 15, 2, 2, 2, 2, 2, 2, 2, 15, 2, 15, 2, 2, 15, 2, 15, 15, 15, 2, 15, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 15, 15, 15, 2, 2, 2, 2, 2, 2, 3, 3, 2, 2, 2, 2, 2, 2])
  
class IPTCNewsPhoto(iptc.IPTCRecord):
  RECORD_NUM = 3
  tags = qdb.QDB()
  tags.addList("name", ["NewsPhotoVersion","IPTCPictureNumber","IPTCImageWidth","IPTCImageHeight","IPTCPixelWidth","IPTCPixelHeight","SupplementalType","ColorRepresentation","InterchangeColorSpace","ColorSequence","ICC_Profile","ColorCalibrationMatrix","LookupTable","NumIndexEntries","ColorPalette","IPTCBitsPerSample","SampleStructure","ScanningDirection","IPTCImageRotation","DataCompressionMethod","QuantizationMethod","EndPoints","ExcursionTolerance","BitsPerComponent","MaximumDensityRange","GammaCompensatedValue"])
  tags.addList("num", [0, 10, 20, 30, 40, 50, 55, 60, 64, 65, 66, 70, 80, 84, 85, 86, 90, 100, 102, 110, 120, 125, 130, 135, 140, 145])
  tags.addList("count", [1, 16, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1])
  tags.addList("data_type", [3, 2, 3, 3, 3, 3, 1, 3, 1, 1, None, None, None, 3, None, 1, 1, 1, 1, 4, 1, None, 1, 1, 3, 3])
  
class IPTCPreObjectData(iptc.IPTCRecord):
  RECORD_NUM = 7
  tags = qdb.QDB()
  tags.addList("name", ["SizeMode", "MaxSubfileSize", "ObjectSizeAnnounced", "MaximumObjectSize"])
  tags.addList("num", [10, 20, 90, 95])
  tags.addList("count", [None, None, None, None])
  tags.addList("data_type", [None, None, None, None])
  
class IPTCObjectData(iptc.IPTCRecord):
  RECORD_NUM = 8
  tags = qdb.QDB()
  tags.addList("name", ["SubFile"])
  tags.addList("num", [10])
  tags.addList("count", [None])
  tags.addList("data_type", [None])
  
class IPTCPostObjectData(iptc.IPTCRecord):
  RECORD_NUM = 9
  tags = qdb.QDB()
  tags.addList("name", ["ConfirmedObjectSize"])
  tags.addList("num", [10])
  tags.addList("count", [None])
  tags.addList("data_type", [None])

class IPTC(metainfofile.MetaInfoBlock, datablock.DataBlock):
  """ Read and write IPTC info. """
  DATA_TYPES = iptc.DATA_TYPES
  
  def __init__(self, fp = None, offset = None, length = None, data = None, big_endian = True):
   
    self.big_endian = big_endian
    
    # Call the DataBlock constructor
    datablock.DataBlock.__init__(self, **{"fp": fp, "offset": offset, "length": length, "data": data})
      
    # We keep an internal map of all the records
    self.records = qdb.QDB()
    self.records.addList("num", [1, 2, 3, 7, 8, 9])
    self.records.addList("name", ["IPTCEnvelope", "IPTCApplication", "IPTCNewsPhoto", "IPTCPreObjectData", "IPTCObjectData", "IPTCPostObjectData"])
    self.records.addList("record", [IPTCEnvelope(big_endian = big_endian), IPTCApplication(big_endian = big_endian), IPTCNewsPhoto(big_endian = big_endian), IPTCPreObjectData(big_endian = big_endian), IPTCObjectData(big_endian = big_endian), IPTCPostObjectData(big_endian = big_endian)])

    # Parse the file
    self.parse()
    
  def parse(self):
    """ Parse the IPTC block. """
    
    # The IPTC data is structured in a very simple way; as a lineary stream of
    # tags and the associated data. Tags can belong to different segments, but
    # this segment number is simply written in front of each tag.
    
    #Each tag starts with the bye 0x1C
    try:
      start_byte = self.read(1)
    except IOError:
      start_byte = None
      
    while (start_byte == "\x1c"):
      # The next byte specifies the record number
      record_num = byteform.btoi(self.read(1))
      
      # Then follows the tag number
      tag_type = byteform.btoi(self.read(1))

      # The next two bytes determine the payload length, or the length of the
      # fields specifying the payload length if we have an extended tag.
      length = byteform.btoi(self.read(2), big_endian = self.big_endian)
      # If the most significant bit is 1, we have an extended tag
      if (length & 32768): # 10000000 00000000
        # We have an extended tag
        length_count = length & 32767 # 01111111 11111111
        length = byteform.btoi(self.read(length_count), big_endian = self.big_endian)

      # Construct the tag and append it to the list
      tag_obj = datablock.DataBlock(self.fp, self.tell() + self.getDataOffset(), length)
      record = self.records.query("num", record_num, "record")
      if (tag_type in record.fields):
        record.fields[tag_type].append(tag_obj)
      else:
        record.fields[tag_type] = [tag_obj]
      
      # Seek to the next read position and read the new first byte
      self.seek(self.tell() + length)
      try:
        start_byte = self.read(1)
      except IOError:
        break
      
  def getBlob(self):
    """ Return the entire IPTC record as binary data blob. """
    
    # The buffer
    out_str = ""
    
    # Iterate over all record numbers. Records in IPTC should be in numerical
    # order.
    for record in self.records.getList("record"):
      out_str += record.getBlob()
    return out_str
    
  def appendTag(self, tag, payload, record = None):
    """ Append a tag to the list of tags. """
  
    rec_num, tag_num = self.__getRecordAndTagNum__(tag)
    if (rec_num):
      self.records.query("num", rec_num, "record").appendTag(tag_num, payload)
