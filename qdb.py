import types

class QDB:
  """ A basic query-able database. This class can functions as such or as a base
      class. Derived classes should implement a number of same-sized lists. For
      normal use these lists can be set by addList(). """
  
  def __init__(self):
    # Check for the proper lengths of all the lists
    self.length = None
    for var_name in dir(self):
      var = eval("self.%s" % var_name)
      if (type(var) == types.ListType):
        self.__checkLength__(var)
  
  def addList(self, list_name, new_list):
    """ Add a list to the current database. """
    
    # Check length
    self.__checkLength__(new_list)
    
    # Add the list
    setattr(self, list_name, new_list)
  
  def query(self, *args):
    """ Make a query to the internal database. This can happen in three ways:
        - key_var_name, condition, return_var_name: return the value of the 
          return_var_name for each case where key_var_name follows the condition.
        - key_var_name, condition: return the indices where the condition
          is true.
        - index, return_var_name: return the value of return_var_name at the
          index. """
    
    # Find out what the user provided us with
    key_var_name    = None
    return_var_name = None
    if (len(args) == 2):
      if (type(args[0]) == types.StringType):
        key_var_name = args[0]
        condition    = args[1]
      else:
        if (type(args[0]) == types.ListType):
          indices = args[0]
        elif (type(args[0]) == types.IntType):
          indices = [args[0]]
        return_var_name = args[1]
    if (len(args) == 3):
      key_var_name    = args[0]
      condition       = args[1]
      return_var_name = args[2]
      
    # Get the list in which we should lookup the return value
    if (return_var_name):
      return_var = getattr(self, return_var_name)
    
    # Construct the list in which we should lookup the index
    if (key_var_name):
      key_var = getattr(self, key_var_name)

      # Find the indices where the condition holds true
      indices = []
      try: index = key_var.index(condition)
      except ValueError: index = None
      while (index != None):
        indices.append(index)
        try: index += key_var[index+1:].index(condition) + 1
        except ValueError: index = None
    
    # If we didn't find any indices, return False
    if (len(indices) == 0):
      return False
    else:
      # If the user specified the name of a list for return values, search this
      # list
      if (return_var_name):
        return_values = []
        for index in indices:
          return_values.append(return_var[index])
            
      # Otherwise, return the indices
      else:
        return_values = indices

    # If we found one return value, return it as such, otherwise, return a list
    if (len(return_values) == 1):
      return return_values[0]
    else:
      return return_values
       
  def setValue(self, key_var_name, condition, target_var_name, value):
    """ Sets the value of target_var_name to value where key_var_name follows
        the condition. """
    # TODO: Should accept index argument, like query does
    
    index = self.query(key_var_name, condition)
    target_var = getattr(self, target_var_name)
    target_var[index] = value
    
  def getList(self, var_name):
    """ Return one of the list, named var_name. """
    return getattr(self, var_name)
    
  def __checkLength__(self, list):
    """ Checks if the length of a list is the same as the others, or sets the
        length if this is not yet known. """
        
    if (not self.length):
      self.length = len(list)
    elif (len(list) != self.length):
      raise "Improper sized list!"
