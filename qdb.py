import types

class QDB:
  """ A basic query-able database. This class functions as a base class. Derived
      classes should implement a number of same-sized lists. """
  
  def __init__(self):
    # Check for the proper lengths of all the lists
    length = None
    for var_name in dir(self):
      var = eval("self.%s" % var_name)
      if (type(var) == types.ListType):
        if (not length):
          length = len(var)
        elif (len(var) != length):
          raise "Not all lists have the same length!"
    
  @classmethod
  def query(cls, return_var_name, key_var_name, condition):
    """ Return the value of the variable named return_var_name for each case
        where the variable called key_var_name has the condition. """
    
    # Construct the lists we should operate on
    return_var = eval("cls.%s" % return_var_name)
    key_var    = eval("cls.%s" % key_var_name)
    
    # Fiund the indices where the condition holds true
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
      # If we found one index, return a single value
      if (len(indices) == 1):
        return return_var[indices[0]]
      # Otherwise, return a list of values
      else:
        values = []
        for index in indices:
          values.append(return_var[index])
        return values      

  @classmethod
  def getList(cls, var_name):
    """ Return one of the list, named var_name. """
    return eval("cls.%s" % var_name)
