import string
import subprocess
from iograph.src.core.IOGraph import *
from exporter.ValgrindDOTExporter import *

#
#  Callstack class
#
###############################################################################
class Callstack:
    def __init__(self, kind, stack, leak=0):
        self.stack = stack
        self.kind = kind
        self.leak=leak

    # compare callstacks (on kind and stack)
    def cmp(self, callstack):
        if self.kind != callstack.kind:
            return False
        size = len(self.stack)
        if size != len(callstack.stack):
            return False
        for i in xrange(0, size):
            if self.stack[i] != callstack.stack[i]:
                return False
        return True

#
#  Callgraph class
#
###############################################################################

class Callgraph:
    def __init__(self, args):
        self.g = Graph() 
        self.g.add_node("ROOT")
        self.callstacks = []
        self.args = args

    def addCallstack(self, cs):
        global undefined
        # addind "level 0" to the call stack
        lvl = 0
        self.callstacks.append(cs) 
        for call in cs.stack:
            if lvl >= self.args.depth: 
                break
            if call=="ROOT":
                continue

            # try to find if the call exists already in the callgraph
            if not self.g.has_node(call):
                self.g.add_node(call)
                self.g.add_arrow(cs.stack[lvl],call)
                self.g.get_arrow(cs.stack[lvl],call).add_attr("leak", cs.leak)
                # color leave and uncolor source
                self.g.get_node(call).add_attr("color", "lightblue")
                self.g.get_node(cs.stack[lvl]).def_attr("color", "none")
            elif not self.g.has_arrow(cs.stack[lvl], call):
                # check if it's a recursive function
                self.g.add_arrow(cs.stack[lvl],call)
                self.g.get_arrow(cs.stack[lvl],call).add_attr("leak", cs.leak)
                # uncolor source
                self.g.get_node(cs.stack[lvl]).def_attr("color", "none")
            else:
                # change the weight of the edge (num of leaked bytes)
                arrow = self.g.get_arrow(cs.stack[lvl],call)
                leaked = arrow.get_attr("leak") 
                arrow.set_attr("leak", leaked + cs.leak)
            lvl += 1

    def diff(self, old_graph):
        # put all new nodes in red
        for node in self.g.get_nodes():
            node_name = node.get_name()
            if not old_graph.g.has_node(node_name):
                node.def_attr("color","red")

        # for each arrow in old graph, update leak 
        for old_arrow in old_graph.g.get_arrows():
            src_name = old_arrow.get_src_node().get_name()
            dst_name = old_arrow.get_dst_node().get_name()

            # update arrow leak if leak present
            new_leak = 0
            if self.g.has_arrow(src_name,dst_name):
                new_leak = self.g.get_arrow(src_name,dst_name).get_attr("leak")
            diff_val = new_leak - old_arrow.get_attr("leak")

            if diff_val == 0:
                continue

            # if there is a difference
            new_src = None
            new_dst = None
            if not self.g.has_node(src_name):
                self.g.add_node(src_name)
                new_src = self.g.get_node( src_name )
                new_src.def_attr("color", "green")
            if not self.g.has_node(dst_name):
                self.g.add_node(dst_name)
                new_dst = self.g.get_node( dst_name )
                new_dst.def_attr("color", "green")
            if not new_src:
                new_src = self.g.get_node( src_name )
            if not new_dst:
                new_dst = self.g.get_node( dst_name )
            if not self.g.has_arrow(src_name, dst_name):
                self.g.add_arrow(src_name,dst_name)

            diff_arrow = self.g.get_arrow(src_name, dst_name)
            diff_arrow.add_attr("leak",diff_val)
            if diff_val > 0:
                diff_arrow.def_attr("color","red")
            elif diff_val < 0:
                diff_arrow.def_attr("color","green")

        # put all red arrows in red
        for new_arrow in self.g.get_arrows():
            src_name = new_arrow.get_src_node().get_name()
            dst_name = new_arrow.get_dst_node().get_name()  
            if not old_graph.g.has_arrow(src_name, dst_name):
                new_arrow.def_attr("color","red")

    def diff_only(self, old_graph):
        # remove all unchanged arrows (or arrow with lower weight)
        for old_arrow in old_graph.g.get_arrows():
            src_name = old_arrow.get_src_node().get_name()
            dst_name = old_arrow.get_dst_node().get_name()
            old_weight = old_arrow.get_attr("leak")

            new_arrow = self.g.get_arrow(src_name, dst_name)
            if new_arrow is None:
                continue

            new_weight = new_arrow.get_attr("leak")
            if new_weight <= old_weight:
                self.g.del_arrow(src_name, dst_name)

        # remove all node that aren't link to an arrow anymore
        # we can not remove element from a list while looping on it 
        nodes_to_be_removed = [n for n in self.g.get_nodes() if not n.has_arrows()]
        for node in nodes_to_be_removed:
            self.g.del_node( node.get_name() )

    # works differently than the 2 previous one. Compare callstacks with the
    # old graph, and return a new graph object
    def diff_ratio(self, old_graph, ratio):
        graph = Callgraph(self.args)

        for old_callstack in old_graph.callstacks:
            for new_callstack in self.callstacks:
                if old_callstack.cmp(new_callstack) and new_callstack.leak !=0:
                    if new_callstack.leak >= old_callstack.leak * ratio:
                        graph.addCallstack( new_callstack )
        return graph

    def demangle(self):
        # get demangled node names
        s = ""
        for n in self.g.nodes:
            s += n.strip("\"") + "\n"
        demangled_nodes = subprocess.Popen(["c++filt", "-p"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE).communicate(s)[0]
        demangled_nodes = demangled_nodes.split("\n")

        # add parameter to each node
        for i,node_name in enumerate(self.g.nodes):
            self.g.get_node(node_name).add_attr("demangled", demangled_nodes[i])

    def draw(self, fname="leak.dot", node="ROOT"):
        # create dot file
        e = ValgrindDOTExporter(self.g, self.args)
        e.add_attr("rankdir", "LR") # add attribute to the exporter
        path = fname
        if( self.args.output_dir ):
            path = self.args.output_dir + "/" + path
        e.export( path + ".dot", fname)
        if self.args.svg:
            try:
                subprocess.call(["dot", "-Tsvg", path+".dot"],stdout=open(path+".svg.bak", 'w'))
                subprocess.call(["rm", path+".dot"])
            except:
                print "Command dot has failed. Ensure your systems has dot installed."
            firstg = True
            f = open(path+".svg", 'w')
            for line in open(path+".svg.bak"):
                if firstg:
                    if line.find("<svg ") >= 0 :
                        f.write("<svg xmlns=\"http://www.w3.org/2000/svg\" xmlns:xlink=\"http://www.w3.org/1999/xlink\">\n")
                        f.write("<script type=\"text/ecmascript\">\n")
                        f.write("<![CDATA[")
                        for liblines in open(sys.path[0]+"/../libs/SVGPan.js"):
                            f.write(liblines);
                        f.write("// ]]>")
                        f.write("</script>\n")
                    elif line.find("<g ") >= 0:
                        f.write(line.replace("graph0","viewport"))
                        firstg = False
                else:
                    f.write(line)
            f.close()      
            subprocess.call(["rm", path+".svg.bak"])


