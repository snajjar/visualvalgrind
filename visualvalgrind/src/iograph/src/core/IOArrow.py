#/usr/bin/env python

from attribute_object import *

class Arrow(attribute_object):
    def __init__(self, src_node, dst_node, name=""):
        self.src_node = src_node
        self.dst_node = dst_node
        self.name = ""
        attribute_object.__init__(self)
    
    def set_name(self, name):
        self.name = name

    def get_name(self):
        return self.name

    def get_src_node(self):
        return self.src_node

    def get_dst_node(self):
        return self.dst_node
