#!/usr/bin/env python

# this class define a group of attributes, to simplify attribution (to a node,
# an arrow, a graph, or every object)

# prefer using "add_attr" method than set_attrs if possible.
# I'm not joking. We know who you are.

class attribute_object(object):
    def __init__(self):
        self.attrs = [] 

    def add_attr(self, name, value):
        self.attrs.append( [name, value] )
    
    def get_attr(self, name):
        for attr in self.attrs:
            if attr[0] == name:
                return attr[1] 
        return None 

    def has_attr(self, name):
        return self.get_attr(name) != None

    # change the whole list of attributes
    def set_attrs(self, attrs):
        self.attrs = attrs

    # search for an attribute and changes its value
    # return True if success, False otherwise
    def set_attr(self, name, value):
        for attr in self.attrs:
            if attr[0] == name:
                attr[1] = value
                return True
        return False

    def def_attr(self, name, value):
        if not self.set_attr(name, value):
            self.add_attr(name, value)
            
