import re

class rex_check(object):
  def __init__(self, pattern):
    self.pattern = pattern
  def __contains__(self, val):
    return re.match(self.pattern, val)
  def __iter__(self):
    return iter(("str", self.pattern))
