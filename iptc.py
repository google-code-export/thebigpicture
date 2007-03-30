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

import datablock, byteform, types, iptcdatatypes, qdb, metainfofile

class IPTCRecord(metainfofile.MetaInfoRecord):
  """ Base class for retrieving data about tags in IPTC records. Derived
      classes should implement the following lists:
      - name : the names of the tags
      - num  : the numbers of the tags
      - count: the number of words every tag should occupy, with None
                    to indicate that this is free
      - type : the numbers of tag data types of the tags, as found in
                iptcdatatypes.TYPES
  """
  
  def __init__(self, **kwargs):
    self.fields = {}
    if ("big_endian" in kwargs):
      self.big_endian = kwargs["big_endian"]
      del kwargs["big_endian"]
    else:
      self.big_endian = True
    datablock.DataBlock.__init__(self, **kwargs)
    
  def getTagPayload(self, tag_num):
    """Returns the payload from a certain tag name or number."""
    
    # Get the tag number
    #tag_num = self.__getTagNum__(tag)

    if (tag_num in self.fields):
      tags = self.fields[tag_num]
    else:
      # If the tag was not found, return False
      return False

    # Decipher the relevant info
    data_type = self.records.query("num", tag_num, "data_type")
    payload = []
    for tag in tags:
      data = tag.getData()
      payload.append(iptcdatatypes.TYPES[data_type].decode(data, self.big_endian))

    # Make sure that single values of each read tag are returned a single value
    # and not as list
    for index in range(len(payload)):
      if (len(payload[index]) == 1):
        payload[index] = payload[index][0]
        
    # If only a single tag was read, return only that value
    if (len(payload) == 1):
      payload = payload[0]
    
    return payload

  def removeTag(self, tag_num):
    """ Remove tag with the specified number. """
    
    self.fields[tag_num] = []

  def setTag(self, tag_num, payload):
    """Sets the payload for a certain tag num or tag name."""

    self.fields[tag_num] = [self.__getTagObj__(tag_num, payload)]

  def appendTag(self, tag_num, payload):
    """ Append a tag with specified tag number and payload. """
    
    if not (tag_num in self.fields):
      self.setTag(tag_num, payload)
    else:
      self.fields[tag_num].append(self.__getTagObj__(tag_num, payload))
      
  def getBlob(self):
    """ Return a binary string representing the IPTC record. """
    
    data_str = ""
    
    for tag_num in self.getTagNums():
      for tag in self.fields[tag_num]:
        data_str += "\x1C" + chr(self.RECORD_NUM) + chr(tag_num)
        data_length = tag.getDataLength()
        if (data_length > 32767):
          # We should encode an extended tag
          data_length = data_length & 32768 # 10000000 00000000
          data_str += byteform.itob(4, 2, big_endian = self.big_endian) # We cannoot encode it in two bytes, encode it in four. Formally this is incorrect, but in practice this will always do
          
        data_str += byteform.itob(data_length, 2, big_endian = self.big_endian)
        data_str += tag.getData()
        
    return data_str

  def __getTagObj__(self, tag_num, payload):
    """ Helper method to prepare a tag object for setTag and appendTag. """
    
    # Get the index and check if we can set this tag
    index = self.records.query("num", tag_num)
    if (index is False):
      raise KeyError, "Tag %d is not known in this IFD!" % tag_num
        
    # Find out the data type for the tag num and make sure it's a list
    data_type = self.records.query(index, "data_type")
    
    # Retrieve the allowed lengths
    count = self.records.query(index, "count")
    if (type(count) == types.ListType):
      min_count, max_count = count
    else:
      min_count = count
      max_count = count
      
    # Check if the payload has enough data
    if (type(payload) not in [types.ListType, types.TupleType, types.StringType]):
      paylaod = [payload]
    if ((len(payload) < min_count) or (len(payload) > max_count)):
      raise "Wrong number of arguments supplied to encode tag %s!" % str(tag_num)

    # Encode the data
    data = iptcdatatypes.TYPES[data_type].encode(payload, self.big_endian)
    
    # If data type is Digits, pad it with zeroes
    if (data_type == 15):
      word_width = iptcdatatypes.TYPES[data_type].word_width
      data = ((min_count * word_width) - len(data)) * "0" + data
      
    return datablock.DataBlock(data = data)    
##class TagList:
##  """ Manage lists of IPTC tags within a record. IPTC blocks can have multiple
##      tags with the same number. """
##      
##  def __init__(self):
##    # Keep a separate list of the tag nums and the tags
##    self.tag_nums = []
##    self.tags     = []
##  
##  def setTag(self, tag_num, tag_obj):
##    """ Set the tag_num to the specified tag, thereby removing all other
##        occurences of that tag. """
##      
##    self.removeTag(tag_num)
##    self.appendTag(tag_num, tag_obj)
##    
##  def appendTag(self, tag_num, tag_obj):
##    """ Append a tag with the specified tag number. """
##    self.tag_nums.append(tag_num)
##    self.tags.append(tag_obj)
##    
##  def getTags(self, tag_num):
##    """ Return a list of tags with the specified number. """
##    
##    if (tag_num in self.tag_nums):
##      # Get a list of indices where the tag can be found
##      indices = self.__getIndices__(tag_num)
##          
##      # Get the tags at the specified indices
##      tags = []
##      for index in indices:
##        tags.append(self.tags[index])
##        
##      return tags
##    return None
##      
##  def removeTag(self, tag_num):
##    """ Remove all tags with the specified tag number. """
##    
##    # Get the indices where the tags reside
##    indices = self.__getIndices__(tag_num)
##
##    # If we delete multiple tags, the indices get mixed up, so we create a copy
##    new_tag_nums = []
##    new_tags     = []
##    for index in range(len(self.tags)):
##      if (index not in indices):
##        new_tag_nums.append(self.tag_nums[index])
##        new_tags.append(self.tags[index])
##    
##    self.tag_nums = new_tag_nums    
##    self.tags     = new_tags
##    
##  def getTagNums(self):
##    """ Return a sorted list of all unique tag numbers. """
##    
##    tag_nums = list(set(self.tag_nums))
##    tag_nums.sort()
##    return tag_nums
##    
##  def __getIndices__(self, tag_num):
##    """ Return a the indices where the specified tag number can be found. """
##    indices = []
##    for index in range(len(self.tag_nums)):
##      if (self.tag_nums[index] == tag_num):
##        indices.append(index)
##    return indices
    

class IPTCEnvelope(IPTCRecord):
  RECORD_NUM = 1
  records = qdb.QDB()
  records.addList("name", ["EnvelopeRecordVersion", "Destination", "FileFormat", "FileVersion", "ServiceIdentifier", "EnvelopeNumber", "ProductID", "EnvelopePriority", "DateSent", "TimeSent", "CodedCharacterSet", "UniqueObjectName", "ARMIdentifier", "ARMVersion"])
  records.addList("num", [0, 5, 20, 22, 30, 40, 50, 60, 70, 80, 90, 100, 120, 122])
  records.addList("count", [1, 1, 1, 1, [0, 10], 8, [0, 32], 1, 8, 11, [0.32], [14, 80], 1, 1])
  records.addList("data_type", [3, 2, 3, 3, 2, 15, 2, 15, 15, 2, 2, 2, 3, 3])

class IPTCApplication(IPTCRecord):
  RECORD_NUM = 2
  records = qdb.QDB()
  records.addList("name", ["ApplicationRecordVersion","ObjectTypeReference","ObjectAttributeReference","ObjectName","EditStatus","EditorialUpdate","Urgency","SubjectReference","Category","SupplementalCategories","FixtureIdentifier","Keywords","ContentLocationCode","ContentLocationName","ReleaseDate","ReleaseTime","ExpirationDate","ExpirationTime","SpecialInstructions","ActionAdvised","ReferenceService","ReferenceDate","ReferenceNumber","DateCreated","TimeCreated","DigitalCreationDate","DigitalCreationTime","OriginatingProgram","ProgramVersion","ObjectCycle","By-line","By-lineTitle","City","Sub-location","Province-State","Country-PrimaryLocationCode","Country-PrimaryLocationName","OriginalTransmissionReference","Headline","Credit","Source","CopyrightNotice","Contact","Caption-Abstract","LocalCaption","Writer-Editor","RasterizedCaption","ImageType","ImageOrientation","LanguageIdentifier","AudioType","AudioSamplingRate","AudioSamplingResolution","AudioDuration","AudioOutcue","JobID","MasterDocumentID","ShortDocumentID","UniqueDocumentID","OwnerID","ObjectPreviewFileFormat","ObjectPreviewFileVersion","ObjectPreviewData","ClassifyState","SimilarityIndex","DocumentNotes","DocumentHistory","ExifCameraInfo"])
  records.addList("num", [0, 3, 4, 5, 7, 8, 10, 12, 15, 20, 22, 25, 26, 27, 30, 35, 37, 38, 40, 42, 45, 47, 50, 55, 60, 62, 63, 65, 70, 75, 80, 85, 90, 92, 95, 100, 101, 103, 105, 110, 115, 116, 118, 120, 121, 122, 125, 130, 131, 135, 150, 151, 152, 153, 154, 184, 185, 186, 187, 188, 200, 201, 202, 225, 228, 230, 231, 232])
  records.addList("count", [1, [3, 67], [4, 68], [0, 64], [0, 64], 2, 1, [13, 236], [0, 3], [0, 32], [0, 32], [0, 64], 3, [0, 64], 8, 11, 8, 11, [0, 256], 2, [0, 10], 8, 8, 8, 11, 8, 11, [0, 32], [0, 10], 1, [0, 32], [0, 32], [0, 32], [0, 32], [0, 32], 3, [0, 64], [0, 32], [0, 256], [0, 32], [0, 32], [0, 128], [0, 128], [0, 2000], [0, 256], [0, 32], 7360, 2, 1, [2, 3], 2, 6, 2, 6, [0, 64], [0, 64], [0, 256], [0, 64], [0, 128], [0, 128], 0, 1, [0, 256000], [0, 64], [0, 32], [0, 1024], [0, 256], [0, 4096]])
  records.addList("data_type", [3, 2, 2, 2, 2, 15, 15, 2, 2, 2, 2, 2, 2, 2, 15, 2, 15, 2, 2, 15, 2, 15, 15, 15, 2, 15, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 15, 15, 15, 2, 2, 2, 2, 2, 2, 3, 3, 2, 2, 2, 2, 2, 2])
  
class IPTCNewsPhoto(IPTCRecord):
  RECORD_NUM = 3
  records = qdb.QDB()
  records.addList("name", ["NewsPhotoVersion","IPTCPictureNumber","IPTCImageWidth","IPTCImageHeight","IPTCPixelWidth","IPTCPixelHeight","SupplementalType","ColorRepresentation","InterchangeColorSpace","ColorSequence","ICC_Profile","ColorCalibrationMatrix","LookupTable","NumIndexEntries","ColorPalette","IPTCBitsPerSample","SampleStructure","ScanningDirection","IPTCImageRotation","DataCompressionMethod","QuantizationMethod","EndPoints","ExcursionTolerance","BitsPerComponent","MaximumDensityRange","GammaCompensatedValue"])
  records.addList("num", [0, 10, 20, 30, 40, 50, 55, 60, 64, 65, 66, 70, 80, 84, 85, 86, 90, 100, 102, 110, 120, 125, 130, 135, 140, 145])
  records.addList("count", [1, 16, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1])
  records.addList("data_type", [3, 2, 3, 3, 3, 3, 1, 3, 1, 1, None, None, None, 3, None, 1, 1, 1, 1, 4, 1, None, 1, 1, 3, 3])
  
class IPTCPreObjectData(IPTCRecord):
  RECORD_NUM = 7
  records = qdb.QDB()
  records.addList("name", ["SizeMode", "MaxSubfileSize", "ObjectSizeAnnounced", "MaximumObjectSize"])
  records.addList("num", [10, 20, 90, 95])
  records.addList("count", [None, None, None, None])
  records.addList("data_type", [None, None, None, None])
  
class IPTCObjectData(IPTCRecord):
  RECORD_NUM = 8
  records = qdb.QDB()
  records.addList("name", ["SubFile"])
  records.addList("num", [10])
  records.addList("count", [None])
  records.addList("data_type", [None])
  
class IPTCPostObjectData(IPTCRecord):
  RECORD_NUM = 9
  records = qdb.QDB()
  records.addList("name", ["ConfirmedObjectSize"])
  records.addList("num", [10])
  records.addList("count", [None])
  records.addList("data_type", [None])

class IPTC(metainfofile.MetaInfoBlock):
  """ Read and write IPTC info. """
  DATA_TYPES = iptcdatatypes.TYPES
  
  def __init__(self, fp = None, offset = None, length = None, data = None, big_endian = True):
   
    self.big_endian = big_endian
    
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
      
      # Seek to the next read position
      #if ((self.tell() + length) < self.getDataLength()):
      self.seek(self.tell() + length)
      #else:
      #  break
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
  def appendTag(self, tag, payload, rec = None):
    """ Append a tag to the list of tags. """
  
    rec_num, tag_num = self.__getRecordAndTagNum__(tag)
    if (rec_num):
      self.records.query("num", rec_num, "record").appendTag(tag_num, payload)

    
##  def setTag(self, tag, payload, record = None):
##    """ Set the specified tag in the specified record to the data, overriding
##        all other occurences of that tag. If record num is omitted, the method
##        will try to figure out which record is meant. """
##        
##    rec_num, tag_num, tag = self.__getSetData__(tag, payload, record = record)
##    if (tag):
##      self.records[rec_num].setTag(tag_num, tag)
##    
##  def appendTag(self, tag, payload, record = None):
##    """ Append the specified tag in the specified record to the data. """
##    
##    rec_num, tag_num, tag = self.__getSetData__(tag, payload, record = record)
##    if (tag):
##      self.records[rec_num].appendTag(tag_num, tag)
##      
##  def __getRecordNum__(self, record):
##    """ Returns the record number based on a record number or name. """
##    
##    # Test numerical input
##    if (type(record) == types.IntType):
##      if record in RECORDS.getList("num"):
##        return record
##      else:
##        raise "Unknown IPTC record %d!" % record
##    # Test text input
##    elif (type(record) == types.StringType):
##      if (record in RECORDS.getList("name")):
##        return RECORDS.query("name", record, "num")
##      else:
##        raise "Unknown IPTC record %s!" % record
##    else:
##      raise "I can't make sense of an IPTC record of type %s!" % type(record)
##
##  def __getRecordAndTagNum__(self, tag, record = None):
##    """ Return the record number and tag number for the supplied tag number or
##        name in the specified record name or number. If record is omitted, the
##        method will search in all records and raises an error if doubles are
##        found. """
##      
##    # If the user didn't specify a record, we search through all records
##    if (record == None):
##      record = RECORDS.getList("num")
##    # Otherwise, we need to have a record number
##    else:
##      record = self.__getRecordNum__(record)
##
##    # Find the possible records
##    found_records = []
##    for rec_num in record:
##      tag_num = RECORDS.query("num", rec_num, "record").getTagNum(tag)
##      if (tag_num != False):
##        found_records.append([rec_num, tag_num])
##
##    # Warn if the tag occurs in multiple records
##    if (len(found_records) == 0):
##      found_records = [[None, None]]
##    elif (len(found_records) > 1):
##      raise "Tag %s occurs in multiple records!" % str(tag)
##      
##    return found_records[0]
##
##  def __getSetData__(self, tag, payload, record = None):
##    """ Return the record number, tag number, and DataBlock object for numeric
##        or name inputs. This method is used by the setTag and appendTag methods.
##    """
##        
##    # Get the record and tag number
##    rec_num, tag_num = self.__getRecordAndTagNum__(tag, record)
##    
##    if ((rec_num != None) and (tag_num != None)):
##      # Encode the data
##      data = RECORDS.query("num", rec_num, "record").encode(tag_num, payload, big_endian = self.big_endian)
##      tag = datablock.DataBlock(data = data)
##    else:
##      raise "No valid destination could be found for tag %s" % str(tag)
##  
##    return [rec_num, tag_num, tag]
