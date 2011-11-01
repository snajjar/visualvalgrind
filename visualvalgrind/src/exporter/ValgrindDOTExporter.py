import os
import sys
from iograph.src.exporter.DOTExporter.DOTExporter import *
from iograph.src.core.IOGraph import *

#
#  Exporter for valgrind graph 
#       redefine some functions
###############################################################################
class ValgrindDOTExporter(DOTExporter):
    def __init__(self, g, args):
        super(ValgrindDOTExporter, self).__init__(g)
        self.args = args

    def export_arrow(self, arrow):
        src_name = arrow.get_src_node().get_name() 
        dst_name = arrow.get_dst_node().get_name() 
        if arrow.has_attr("color"):
            self.f.write(src_name + " -> " + dst_name +
                    " [label="+str(arrow.get_attr("leak")) + ", "\
                            "color="+str(arrow.get_attr("color"))+"]\n")
        else: 
            self.f.write(src_name + " -> " + dst_name +
                    " [label="+str(arrow.get_attr("leak")) + "]\n")

    def export_node(self, node):
        name = node.get_name() if not self.args.demangle else "\"" + node.get_attr("demangled") + "\""
        if node.has_attr("color") and str(node.get_attr("color")) != "none" :
            self.f.write(name + " [color="+str(node.get_attr("color")) + ", style=filled]\n")
        else: 
            self.f.write(name + '\n')


