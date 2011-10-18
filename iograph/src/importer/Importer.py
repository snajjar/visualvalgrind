# !/usr/bin/env python


import os
import sys
sys.path.append( os.path.join(os.getcwd(), "../core"))
from IOGraph import *

class Method_not_overridden(Exception):
    def __init__(self, s):
        self.s = s
    def __str__(self):
        return "Method " + s + " is not overridden !"

class Importer(object):
    def __init__(self, fname):
        with open(fname, 'r') as f: 
            self.lines = f.readlines()

    # return a node "string" depending of the format of the file
    # return None if no more node
    def read_node_str(self):
        raise Method_not_overridden("read_node_str")

    # return a arrow "string" depending of the format of the file
    # return None if no more node
    def read_arrow_str(self):
        raise Method_not_overridden("read_arrow_str")

    def import_node(self, g, node_str):
        raise Method_not_overridden("import_node")

    def import_arrow(self, g, arrow_str):
        raise Method_not_overridden("import_arrow")

    def get_graph(self):
        g = Graph()
        node_str = self.read_node_str():
        if node_str:
            self.import_node(g, node_str)
        arrow_str = self.read_arrow_str():
        if arrow_str:
            self.import_arrow(g, arrow_str)
        return g
