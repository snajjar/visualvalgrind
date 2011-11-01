# !/usr/bin/env python

import sys
from iograph.src.core.attribute_object import *

class DOTExporter(attribute_object):
    def __init__(self, graph):
        self.graph = graph
        attribute_object.__init__(self)

    def export(self, f_name, name="G"):
        # close f when done
        with open(f_name, 'w') as self.f: 
            self.f.write("digraph " + name + " {\n"); 
            for attr in self.attrs:
                self.f.write( attr[0] + "=" + attr[1] + "\n" )
            self.export_nodes()
            self.export_arrows()
            self.f.write("}\n")
        
    def export_nodes(self):
        nodes = self.graph.get_nodes()
        for node in nodes:
            self.export_node(node)

    def export_arrows(self):
        arrows = self.graph.get_arrows()
        for arrow in arrows:
            self.export_arrow(arrow)

    # overridable functions
    def export_node(self, node):
        self.f.write(node.get_name() + '\n')

    def export_arrow(self, arrow):
        src_node = arrow.get_src_node()
        dst_node = arrow.get_dst_node()
        self.f.write(src_node.get_name() + " -> " + dst_node.get_name() + '\n')


