#!usr/bin/env python

from IOArrow import *
from IONode import *
from attribute_object import *

class Node_not_deletable(Exception):
    def __init__(self, name, reason):
        self.name = name
        self.reason = reason
    def __str__(self):
        return "Node  " + name + "cannot be deleted : " + self.reason

 
class Arrow_not_deletable(Exception):
    def __init__(self, n1name, n2name, reason):
        self.n1name = n1name
        self.n2name = n2name
        self.reason = reason
    def __str__(self):
        s = "Arrow between  " + n1name + " and " + n2name 
        s += "cannot be deleted : " + self.reason
        return s

class Arrow_not_creable(Exception):
    def __init__(self, n1name, n2name, reason):
        self.n1name = n1name
        self.n2name = n2name
        self.reason = reason
    def __str__(self):
        s = "Arrow between  " + n1name + " and " + n2name 
        s += "cannot be created : " + self.reason
        return s

class Graph(attribute_object):
    def __init__(self, name = ""):
        self.name = ""
        self.nodes = {}
        self.arrows = {}
        attribute_object.__init__(self)

    def add_node(self, name):
        self.nodes[name] = Node(name)

    # return the node object if node exist. Return None otherwise
    def get_node(self, name):
        if self.has_node(name):
            return self.nodes[name]
        return None

    def has_node(self,name):
        return name in self.nodes.keys()

    def add_arrow(self, n1name, n2name, name = ""):
        node1 = self.get_node(n1name)
        node2 = self.get_node(n2name)
        if node1 is None:
            s = "Node " + n1name + " not found"
            raise Arrow_not_creable(n1name, n2name, s)
        if node2 is None:
            s = "Node " + n2name + " not found"
            raise Arrow_not_creable(n1name, n2name, s)
        arrow = Arrow(node1, node2, name)
        node1.add_out_arrow(arrow)
        node2.add_in_arrow(arrow)
        self.arrows[(n1name,n2name)] = arrow
   
    def get_arrow(self, n1name, n2name):
        node1 = self.get_node(n1name)
        node2 = self.get_node(n2name)
        if node1 is None or node2 is None:
            return None
        if self.has_arrow(n1name,n2name):
            return self.arrows[(n1name,n2name)]
        return None

    def has_arrow(self, n1name, n2name):
        return (n1name, n2name) in self.arrows.keys()

    def del_arrow(self, n1name, n2name):
        node1 = self.get_node(n1name)
        node2 = self.get_node(n2name)
        if node1 is None:
            s = "Node " + n1name + " not found"
            raise Arrow_not_deletable(n1name, n2name, s)
        if node2 is None:
            s = "Node " + n2name + " not found"
            raise Arrow_not_deletable(n1name, n2name, s)
        arrow = self.get_arrow( n1name, n2name )
        if arrow is None:
            raise Arrow_not_deletable(n1name, n2name, "Arrow doesn't exist")
        node1.del_out_arrow(n2name)
        node2.del_in_arrow(n1name)
        del self.arrows[(n1name,n2name)]

    def del_node(self, node_name):
        node = self.get_node(node_name)
        if node is None:
            raise Node_not_deletable(node_name, "Node not found")
        if node.has_arrows():
            raise Node_not_deletable(node_name, "Node has arrows")
        del self.nodes[node_name]

    def get_nodes(self):
        return self.nodes.values()

    def get_arrows(self):
        return self.arrows.values()




