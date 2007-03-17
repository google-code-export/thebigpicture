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

import tag, byteform

# The possible IPTC records. This data is taken from the Exiftool documentation
RECORDS = [1, 2, 3, 7, 8, 9]
REC_NUMS = {
  "IPTCEnvelope":       1,
  "IPTCApplication":    2,
  "IPTCNewsPhoto":      3,
  "IPTCPreObjectData":  7,
  "IPTCObjectData":     8,
  "IPTCPostObjectData": 9
}

class TagList:
  """ Manage lists of IPTC tags within a record. IPTC blocks can hav multiple
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
class IPTC(tag.Tag):
  """ Read and write IPTC info. """
  
  def __init__(self, fp, file_offset, length, big_endian = True):
    tag.Tag.__init__(self, fp = fp, offset = file_offset, length = length)
    
    self.big_endian = big_endian
    
    # We keep an internal map of all the records
    self.records = {}
    for rec_num in RECORDS:
      self.records[rec_num] = TagList()
      
    # Parse the file
    self.parse()
    
  def parse(self):
    """ Parse the IPTC block. """
    
    # The IPTC data is structured in a very simple way; as a lineary stream of
    # tags and the associated data. Tags can belong to different segments, but
    # this segment number is simply written in front of each tag.
    
    #Each tag starts with the bye 0x1C
    while (self.read(1) == "\x1c"):
      # The next byte specifies the record number
      record_num = byteform.btoi(self.read(1))
      
      # Then follows the tag number
      tag_type = byteform.btoi(self.read(1))

      # The next two bytes determine the payload length
      length = byteform.btoi(self.read(2))
      
      # Construct the tag and append it to the list
      tag_obj = tag.Tag(self.fp, self.tell() + self.getDataOffset(), length)
      self.records[record_num].appendTag(tag_type, tag_obj)
      
      # Seek to the next read position
      if ((self.tell() + length) < self.getDataLength()):
        self.seek(self.tell() + length)
      else:
        break
      
  def getBlob(self):
    """ Return the entire IPTC record as binary data blob. """
    
    # The buffer
    out_str = ""
    
    # Iterate over all records
    for rec_num in RECORDS:
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
    
  def getTag(self, record_num, tag_num):
    """ Return the tag data with the specified number from the specified record.
    """
    
    if (record_num in self.records):
      # Get the tags
      tags = self.records[record_num].getTags(tag_num)
    
      # Get the tag data
      data = []
      for tag in tags:
        data.append(tag.getData())
        
      return data
    return None
    
  def setTag(self, record_num, tag_num, data):
    """ Set the specified tag in the specified record to the data, overriding
        all other occurences of that tag. """
    if (record_num in self.records):
      tag_obj = tag.Tag(data = data)
      self.records[record_num].setTag(tag_num, tag_obj)
    
  def appendTag(self, record_num, tag_num, data):
    """ Append the specified tag in the specified record to the data. """
    if (record_num in self.records):
      tag_obj = tag.Tag(data = data)
      self.records[record_num].appendTag(tag_num, tag_obj)
