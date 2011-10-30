#/usr/bin/env python

from IOArrow import *
from attribute_object import *

class Node(attribute_object):
    def __init__(self, name):
        self.name = name
        self.in_arrows = {}  # arrows arriving in this node
        self.out_arrows = {} # arrows going to another node
        attribute_object.__init__(self)
    
    def set_name(self, name):
        self.name = name

    def get_name(self):
        return self.name

    def add_in_arrow(self, arrow):
        self.in_arrows[arrow.get_src_node().get_name()] = arrow
    
    def add_out_arrow(self, arrow):
        self.out_arrows[arrow.get_dst_node().get_name()] = arrow

    def has_in_arrow(self, node_name):
        return node_name in self.in_arrows.keys()

    def has_out_arrow(self, node_name):
        return node_name in self.out_arrows.keys()

    def has_in_arrows(self):
        for k in self.in_arrows.keys():
            return True
        return False

    def has_out_arrows(self):
        for k in self.out_arrows.keys():
            return True
        return False

    def has_arrows(self):
        return self.has_in_arrows() or self.has_out_arrows()

    def del_in_arrow(self, node_name):
        if self.has_in_arrow(node_name):
            del self.in_arrows[node_name]
            return True
        return False

    def del_out_arrow(self, node_name):
        if self.has_out_arrow(node_name):
            del self.out_arrows[node_name]
            return True
        return False

    def get_in_arrows(self):
        return self.in_arrows.values()

    def get_out_arrows(self):
        return self.out_arrows.values()
