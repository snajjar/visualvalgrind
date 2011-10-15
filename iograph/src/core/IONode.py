#/usr/bin/env python

from IOArrow import *
from attribute_object import *

class Node(attribute_object):
    def __init__(self, name):
        self.name = name
        self.in_arrows = []  # arrows arriving in this node
        self.out_arrows = [] # arrows going to another node
        attribute_object.__init__(self)
    
    def set_name(self, name):
        self.name = name

    def get_name(self):
        return self.name

    def add_in_arrow(self, arrow):
        self.in_arrows.append(arrow)
    
    def add_out_arrow(self, arrow):
        self.out_arrows.append(arrow)

    def has_in_arrow(self, node_name):
        for n in self.in_arrows:
            if n.get_name() == node_name:
                return True
        return False

    def has_out_arrow(self, node_name):
        for n in self.out_arrows:
            if n.get_name() == node_name:
                return True
        return False

    def del_in_arrow(self, node_name):
        for n in self.in_arrows:
            if n.get_name() == node_name:
                self.in_arrows.remove(n)
                return True
        return False

    def del_out_arrow(self, node_name):
        for n in self.out_arrows:
            if n.get_name() == node_name:
                self.in_arrows.remove(n)
                return True
        return False

    def get_in_arrows(self):
        return self.in_arrows

    def get_out_arrows(self):
        return self.out_arrows
