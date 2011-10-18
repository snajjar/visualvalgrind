# !/usr/bin/env python

class XMLImporter(object):
    def __init__(self, graph):
        self.graph = graph

    def export(self, f_name):
        # close f when done
        with open(f_name, 'w') as f: 
            f.write("digraph G {\n"); 
            self.export_nodes(f)
            self.export_arrows(f)
            f.write("}\n")
        
    def export_nodes(self, f):
        nodes = self.graph.get_nodes()
        for node in nodes:
            f.write(node.get_name() + '\n')

    def export_arrows(self, f):
        arrows = self.graph.get_arrows()
        for arrow in arrows:
            src_node = arrow.get_src_node()
            dst_node = arrow.get_dst_node()
            f.write(src_node.get_name() + " -> " + dst_node.get_name() + '\n')
