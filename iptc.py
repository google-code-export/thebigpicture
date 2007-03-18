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

import datablock, byteform, types, iptcdatatypes

class IPTCRecord:
  """ Base class for retrieving data about tags in IPTC records. Derived
      classes should implement the following lists:
      - names : the names of the tags
      - nums  : the numbers of the tags
      - counts: the number of words every tag should occupy, with None
                    to indicate that this is free
      - types : the numbers of tag data types of the tags, as found in
                iptcdatatypes.TYPES
  """
  
  @classmethod
  def getTagNum(self, tag):
    """ Returns a tag number when fed a tag number or name, or None if it
        doesn't exist within the current record. """
        
    ret = None
    
    if (type(tag) == types.IntType):
      # We have a tag number as user input
      if tag in self.nums:
        ret = tag
    elif (type(tag) == types.StringType):
      # We have a tag name, search the number for it
      try:
        index = self.names.index(tag)
        ret = self.nums[index]
      except ValueError:
        pass
  
    return ret

  @classmethod
  def getDataType(self, tag):
    """ Return the data type for a certain tag (name or number). """
    tag_num   = self.getTagNum(tag)
    data_type = self.data_types(self.tag_nums.index(tag_num))
    return data_type

  @classmethod
  def getCount(self, tag):
    """ Return the count for a certain tag (name or number), if any, or None
        if otherwise. """
    tag_num = self.getTagNum(tag)
    count   = self.data_types(self.tag_counts.index(tag_num))
    return count

  @classmethod
  def encode(self, tag, payload, big_endian = True):
    """ Encode the data according to the specifications of the tag. """
    tag_num = self.getTagNum(tag)
    index   = self.nums.index(tag_num)
    data    = iptcdatatypes.TYPES[self.types[index]].encode(payload, is_big_endian = big_endian)
    return data

  @classmethod
  def decode(self, tag, data, big_endian = True):
    """ Encode the data according to the specifications of the tag. """
    tag_num = self.getTagNum(tag)
    index   = self.nums.index(tag_num)
    payload = iptcdatatypes.TYPES[self.types[index]].decode(data, is_big_endian = big_endian)
    return payload

class IPTCEnvelope(IPTCRecord):
  names  = ["EnvelopeRecordVersion", "Destination", "FileFormat", "FileVersion", "ServiceIdentifier", "EnvelopeNumber", "ProductID", "EnvelopePriority", "DateSent", "TimeSent", "CodedCharacterSet", "UniqueObjectName", "ARMIdentifier", "ARMVersion"]
  nums   = [0, 5, 20, 22, 30, 40, 50, 60, 70, 80, 90, 100, 120, 122]
  counts = [1, 1, 1, 1, [0, 10], 8, [0, 32], 1, 8, 11, [0.32], [14, 80], 1, 1]
  types  = [3, 2, 3, 3, 2, 15, 2, 15, 15, 2, 2, 2, 3, 3]

class IPTCApplication(IPTCRecord):
  names  = ["ApplicationRecordVersion","ObjectTypeReference","ObjectAttributeReference","ObjectName","EditStatus","EditorialUpdate","Urgency","SubjectReference","Category","SupplementalCategories","FixtureIdentifier","Keywords","ContentLocationCode","ContentLocationName","ReleaseDate","ReleaseTime","ExpirationDate","ExpirationTime","SpecialInstructions","ActionAdvised","ReferenceService","ReferenceDate","ReferenceNumber","DateCreated","TimeCreated","DigitalCreationDate","DigitalCreationTime","OriginatingProgram","ProgramVersion","ObjectCycle","By-line","By-lineTitle","City","Sub-location","Province-State","Country-PrimaryLocationCode","Country-PrimaryLocationName","OriginalTransmissionReference","Headline","Credit","Source","CopyrightNotice","Contact","Caption-Abstract","LocalCaption","Writer-Editor","RasterizedCaption","ImageType","ImageOrientation","LanguageIdentifier","AudioType","AudioSamplingRate","AudioSamplingResolution","AudioDuration","AudioOutcue","JobID","MasterDocumentID","ShortDocumentID","UniqueDocumentID","OwnerID","ObjectPreviewFileFormat","ObjectPreviewFileVersion","ObjectPreviewData","ClassifyState","SimilarityIndex","DocumentNotes","DocumentHistory","ExifCameraInfo"]
  nums   = [0, 3, 4, 5, 7, 8, 10, 12, 15, 20, 22, 25, 26, 27, 30, 35, 37, 38, 40, 42, 45, 47, 50, 55, 60, 62, 63, 65, 70, 75, 80, 85, 90, 92, 95, 100, 101, 103, 105, 110, 115, 116, 118, 120, 121, 122, 125, 130, 131, 135, 150, 151, 152, 153, 154, 184, 185, 186, 187, 188, 200, 201, 202, 225, 228, 230, 231, 232]
  counts = [1, [3, 67], [4, 68], [0, 64], [0, 64], 2, 1, [13, 236], [0, 3], [0, 32], [0, 32], [0, 64], 3, [0, 64], 8, 11, 8, 11, [0, 256], 2, [0, 10], 8, 8, 8, 11, 8, 11, [0, 32], [0, 10], 1, [0, 32], [0, 32], [0, 32], [0, 32], [0, 32], 3, [0, 64], [0, 32], [0, 256], [0, 32], [0, 32], [0, 128], [0, 128], [0, 2000], [0, 256], [0, 32], 7360, 2, 1, [2, 3], 2, 6, 2, 6, [0, 64], [0, 64], [0, 256], [0, 64], [0, 128], [0, 128], 0, 1, [0, 256000], [0, 64], [0, 32], [0, 1024], [0, 256], [0, 4096]]
  types  = [3, 2, 2, 2, 2, 15, 15, 2, 2, 2, 2, 2, 2, 2, 15, 2, 15, 2, 2, 15, 2, 15, 15, 15, 2, 15, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 15, 15, 15, 2, 2, 2, 2, 2, 2, 3, 3, 2, 2, 2, 2, 2, 2]
  
class IPTCNewsPhoto(IPTCRecord):
  names  = ["NewsPhotoVersion","IPTCPictureNumber","IPTCImageWidth","IPTCImageHeight","IPTCPixelWidth","IPTCPixelHeight","SupplementalType","ColorRepresentation","InterchangeColorSpace","ColorSequence","ICC_Profile","ColorCalibrationMatrix","LookupTable","NumIndexEntries","ColorPalette","IPTCBitsPerSample","SampleStructure","ScanningDirection","IPTCImageRotation","DataCompressionMethod","QuantizationMethod","EndPoints","ExcursionTolerance","BitsPerComponent","MaximumDensityRange","GammaCompensatedValue"]
  nums   = [0, 10, 20, 30, 40, 50, 55, 60, 64, 65, 66, 70, 80, 84, 85, 86, 90, 100, 102, 110, 120, 125, 130, 135, 140, 145]
  counts = [1, 16, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
  types  = [3, 2, 3, 3, 3, 3, 1, 3, 1, 1, None, None, None, 3, None, 1, 1, 1, 1, 4, 1, None, 1, 1, 3, 3]
  
class IPTCPreObjectData(IPTCRecord):
  names  = ["SizeMode", "MaxSubfileSize", "ObjectSizeAnnounced", "MaximumObjectSize"]
  nums   = [10, 20, 90, 95]
  counts = [None, None, None, None]
  types  = [None, None, None, None]
  
class IPTCObjectData(IPTCRecord):
  names  = ["SubFile"]
  nums   = [10]
  counts = [None]
  types  = [None]
  
class IPTCPostObjectData(IPTCRecord):
  names  = ["ConfirmedObjectSize"]
  nums   = [10]
  counts = [None]
  types  = [None]
  
# The possible IPTC record names and numbers. This data is taken from the Exiftool documentation
REC_NUMS  = [1, 2, 3, 7, 8, 9]
REC_NAMES = ["IPTCEnvelope", "IPTCApplication", "IPTCNewsPhoto", "IPTCPreObjectData", "IPTCObjectData", "IPTCPostObjectData"]
RECORDS   = [IPTCEnvelope, IPTCApplication, IPTCNewsPhoto, IPTCPreObjectData, IPTCObjectData, IPTCPostObjectData]

class TagList:
  """ Manage lists of IPTC tags within a record. IPTC blocks can have multiple
      tags with the same number. """
      
  def __init__(self):
    # Keep a separate list of the tag nums and the tags
    self.tag_nums = []
    self.tags     = []
  
  def setTag(self, tag_num, tag_obj):
    """ Set the tag_num to the specified tag, thereby removing all other
        occurences of that tag. """
      
    self.removeTag(tag_num)
    self.appendTag(tag_num, tag_obj)
    
  def appendTag(self, tag_num, tag_obj):
    """ Append a tag with the specified tag number. """
    self.tag_nums.append(tag_num)
    self.tags.append(tag_obj)
    
  def getTags(self, tag_num):
    """ Return a list of tags with the specified number. """
    
    if (tag_num in self.tag_nums):
      # Get a list of indices where the tag can be found
      indices = self.__getIndices__(tag_num)
          
      # Get the tags at the specified indices
      tags = []
      for index in indices:
        tags.append(self.tags[index])
        
      return tags
    return None
      
  def removeTag(self, tag_num):
    """ Remove all tags with the specified tag number. """
    
    # Get the indices where the tags reside
    indices = self.__getIndices__(tag_num)

    # If we delete multiple tags, the indices get mixed up, so we create a copy
    new_tag_nums = []
    new_tags     = []
    for index in range(len(self.tags)):
      if (index not in indices):
        new_tag_nums.append(self.tag_nums[index])
        new_tags.append(self.tags[index])
    
    self.tag_nums = new_tag_nums    
    self.tags     = new_tags
    
  def getTagNums(self):
    """ Return a sorted list of all unique tag numbers. """
    
    tag_nums = list(set(self.tag_nums))
    tag_nums.sort()
    return tag_nums
    
  def __getIndices__(self, tag_num):
    """ Return a the indices where the specified tag number can be found. """
    indices = []
    for index in range(len(self.tag_nums)):
      if (self.tag_nums[index] == tag_num):
        indices.append(index)
    return indices
    
class IPTC(datablock.DataBlock):
  """ Read and write IPTC info. """
  
  def __init__(self, fp = None, file_offset = None, length = None, big_endian = True):
    datablock.DataBlock.__init__(self, fp = fp, offset = file_offset, length = length)
    
    self.big_endian = big_endian
    
    # We keep an internal map of all the records
    self.records = {}
    for rec_num in REC_NUMS:
      self.records[rec_num] = TagList()
      
    # Parse the file
    self.parse()
    
  def parse(self):
    """ Parse the IPTC block. """
    
    # The IPTC data is structured in a very simple way; as a lineary stream of
    # tags and the associated data. Tags can belong to different segments, but
    # this segment number is simply written in front of each tag.
    
    #Each tag starts with the bye 0x1C
    while (self.tell() < self.getDataLength()) and (self.read(1) == "\x1c"):
      # The next byte specifies the record number
      record_num = byteform.btoi(self.read(1))
      
      # Then follows the tag number
      tag_type = byteform.btoi(self.read(1))

      # The next two bytes determine the payload length
      length = byteform.btoi(self.read(2))
      
      # Construct the tag and append it to the list
      tag_obj = datablock.DataBlock(self.fp, self.tell() + self.getDataOffset(), length)
      self.records[record_num].appendTag(tag_type, tag_obj)
      
      # Seek to the next read position
      #if ((self.tell() + length) < self.getDataLength()):
      self.seek(self.tell() + length)
      #else:
      #  break
      
  def getBlob(self):
    """ Return the entire IPTC record as binary data blob. """
    
    # The buffer
    out_str = ""
    
    # Iterate over all REC_NUMS
    for rec_num in REC_NUMS:
      # Iterate over all tags in the record
      for tag_num in self.records[rec_num].getTagNums():
        # Iterate over all the tags with that tag number
        for tag_obj in self.records[rec_num].getTags(tag_num):
          # Write 0x1C, the record number and the tag number
          out_str += "\x1C"
          out_str += byteform.itob(rec_num, 1)
          out_str += byteform.itob(tag_num, 1)
          
          # Write the length
          out_str += byteform.itob(tag_obj.getDataLength(), 2, self.big_endian)
          
          # Write the data
          out_str += tag_obj.getData()
          
    return out_str
    
  def getTag(self, tag, record = None):
    """ Return the tag data with the specified number from the specified record.
    """
    
    # Get the record and tag nums
    record_num, tag_num = self.__getRecordAndTagNum__(tag, record)

    if (record_num):
      # Get the tags
      tags = self.records[record_num].getTags(tag_num)
    
      # Get the tag data
      data = []
      for tag in tags:
        data.append(tag.getData())
        
      return data
    return None
    
  def setTag(self, tag, payload, record = None):
    """ Set the specified tag in the specified record to the data, overriding
        all other occurences of that tag. If record num is omitted, the method
        will try to figure out which record is meant. """
        
    rec_num, tag_num, tag = self.__getSetData__(tag, payload, record = record)
    if (tag):
      print self.records
      self.records[rec_num].setTag(tag_num, tag)
    
  def appendTag(self, tag, payload, record = None):
    """ Append the specified tag in the specified record to the data. """
    
    rec_num, tag_num, tag = self.__getSetData__(tag, payload, record = record)
    if (tag):
      self.records[rec_num].appendTag(tag_num, tag)
      
  def __getRecordNum__(self, record):
    """ Returns the record number based on a record number or name. """
    
    # Test numerical input
    if (type(record) == types.IntType):
      if record in REC_NUMS:
        return record
      else:
        raise "Unknown IPTC record %d!" % record
    # Test text input
    elif (type(record) == types.StringType):
      if (record in REC_NAMES):
        return REC_NUMS[REC_NAMES.index(record)]
      else:
        raise "Unknown IPTC record %s!" % record
    else:
      raise "I can't make sense of an IPTC record of type %s!" % type(record)

  def __getRecordAndTagNum__(self, tag, record = None):
    """ Return the record number and tag number for the supplied tag number or
        name in the specified record name or number. If record is omitted, the
        method will search in all records and raises an error if doubles are
        found. """
      
    # If the user didn't specify a record, we search through all records
    if (record == None):
      record = REC_NUMS
    # Otherwise, we need to have a record number
    else:
      record = self.__getRecordNum__(record)

    # Find the possible records
    found_records = []
    for rec_num in record:
      tag_num = RECORDS[REC_NUMS.index(rec_num)].getTagNum(tag)
      if (tag_num != None):
        found_records.append([rec_num, tag_num])

    # Warn if the tag occurs in multiple records
    if (len(found_records) == 0):
      found_records = [[None, None]]
    elif (len(found_records) > 1):
      raise "Tag %s occurs in multiple records!" % str(tag)
      
    return found_records[0]

  def __getSetData__(self, tag, payload, record = None):
    """ Return the record number, tag number, and DataBlock object for numeric
        or name inputs. This method is used by the setTag and appendTag methods.
    """
        
    # Get the record and tag number
    rec_num, tag_num = self.__getRecordAndTagNum__(tag, record)
    
    if ((rec_num != None) and (tag_num != None)):
      # Encode the data
      data = RECORDS[REC_NUMS.index(rec_num)].encode(tag_num, payload, big_endian = self.big_endian)
      tag = datablock.DataBlock(data = data)
    else:
      raise "No valid destination could be found for tag %s" % str(tag)
  
    return [rec_num, tag_num, tag]
