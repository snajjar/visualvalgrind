#!/usr/bin/env python
import os
import sys
import string
import xml.parsers.expat
import subprocess
import re

# Import IOGraph
import sys
sys.path.append('../iograph/src/core')
sys.path.append('../iograph/src/exporter/DOTExporter')

# Import pygraph
from IOGraph import *
from DOTExporter import *

# raise that exception in case of parsing error
class EndParsingError(Exception):
    pass

#
#  Exporter for valgrind graph 
#       redefine some functions
###############################################################################
class ValgrindDOTExporter(DOTExporter):

    def export_arrow(self, arrow):
        src_name = arrow.get_src_node().get_name() 
        dst_name = arrow.get_dst_node().get_name() 
        if arrow.has_attr("color"):
           self.f.write(src_name + " -> " + dst_name +
                " [label="+str(arrow.get_attr("leak")) + ", color="+str(arrow.get_attr("color"))+"]\n")
        else: 
            self.f.write(src_name + " -> " + dst_name +
                " [label="+str(arrow.get_attr("leak")) + "]\n")

    def export_node(self, node):
        if node.has_attr("color") and str(node.get_attr("color")) != "none" :
            self.f.write(node.get_name() +
                " [color="+str(node.get_attr("color")) + ", style=filled]\n")
        else: 
            self.f.write(node.get_name() + '\n')

#
#  parsing from xml file
#
###############################################################################

# init some values
leakedbytes = "0"  # init that value
in_leakedbytes = False
kind = ""
in_kind = False
undefined=1

# build graph name and attributes
def compute_node_name_attr(func):
    global writeFileName
    global undefined
    shape = "note"
    fontsize = "9"
    font = ""
    fname = func[0]
    ffile = func[3]
    fline = func[2]

    # don't loose track of undefined function, make them have a different name
    if fname=="":
        fname="<undefined "+str(undefined)+">"
        undefined += 1

    # if user wants file and line number, give it to him
    if writeFileName:
        label=fname
        if ffile!="" and fline!="":
            label+="\\n"+ffile+":"+fline
        else:
            label = fname
    else:
        label = fname
    return "\"" + label + "\""

# process callstack add the callstack to the good graph, depending on the kind
# of error. If the kind is new, a new graph is created
def process_callstack(kind, callstack, leakedbyte):
    global g, depthMax, separate_kinds

    if kind=="":
        return

    # search if the kind exists and if so, add to the graph
    if separate_kinds:
        for graph in g:
            if graph[0] == kind:
                graph[1].addCallStack(callstack, int(leakedbytes))
                return

        # if the kind doesn't exist yet, create it
        graph = callgraph(depthMax) 
        graph.addCallStack(callstack, int(leakedbytes))
        g.append( [kind, graph] )
    else:
        callstack.insert(0, kind) 
        g.addCallStack(callstack, int(leakedbytes))

def begin_stack():
    global parsing, call, stack, in_call, in_stack
    in_stack = True 
    stack = [] 

def end_stack():
    global stack, in_stack, leakedbytes
    global kind
    in_stack = False
    # build the call stack and add it to graph
    callstack = []
    for func in stack:
        node_name = compute_node_name_attr(func)
        callstack.append(node_name)
    process_callstack(kind, callstack, int(leakedbytes))
    stack = []

def begin_call():
    global call, in_call
    in_call = True
    call = ['' for i in xrange(4)]

def end_call():
    global stack, call, in_call
    in_call = False
    stack.append(call)
    call = [] 

def begin_error():
    global in_error
    in_error = True

def end_error():
    global in_error, leakedbytes
    in_error = False 
    leakedbytes = 0

def begin_leakedbytes():
    global in_leakedbytes
    in_leakedbytes = True

def end_leakedbytes():
    global in_leakedbytes
    in_leakedbytes = False 

def begin_kind():
    global in_kind
    in_kind = True

def end_kind():
    global in_kind
    in_kind = False


def add_call_attribute(value):
    global call, parsing, demangle
    if parsing=="fn": 
        # demangle the function name
        if demangle:
            fn = subprocess.Popen(["c++filt",value,"-p"],stdout=subprocess.PIPE).communicate()[0]
            fn = fn.strip(" \r\n") 
        else:
            fn = value.strip(" \r\n")
        if len(fn)>truncateVal:
            fn = fn[:truncateVal]+".."
        call[0]= fn
    if parsing=="dir": 
        call[1]=value
    if parsing=="line": 
        call[2]=value
    if parsing=="file": 
        call[3]=value


# 3 handlers that are called when parsing xml
def xml_start_element(name, attr):
    global parsing
    parsing = name
    if name=="stack":
        begin_stack()
    if name=="frame":
        begin_call()
    if name=="error":
        begin_error()
    if name=="leakedbytes":
        begin_leakedbytes()
    if name=="kind":
        begin_kind()

def xml_handle_data(data):
    global in_call, in_leakedbytes, leakedbytes, in_kind, kind
    if data=='\n':
        return
    
    stripped_data = data.strip(" \r\n")
    if in_call:
        if stripped_data != "":
            add_call_attribute(stripped_data)
    if in_leakedbytes:
        leakedbytes = stripped_data
    if in_kind:
        kind = stripped_data

def xml_end_element(name):
    global parsing
    parsing = ""
    if name=="stack":
        end_stack()
    if name=="frame":
        end_call()
    if name=="error":
        end_error()
    if name=="leakedbytes":
        end_leakedbytes()
    if name=="kind":
        end_kind()

def importXmlFile(fname):
    # init the parser
    p = xml.parsers.expat.ParserCreate()
    p.StartElementHandler = xml_start_element
    p.EndElementHandler = xml_end_element
    p.CharacterDataHandler = xml_handle_data

    # first round just to create all global var
    begin_stack()
    begin_call()
    end_call()
    end_stack()

    # parse the file 
    f = open(fname)
    xmlContent = f.read()
    xmlContent = re.sub("\&.*;", "", xmlContent) # remove &amp; and stuff like that
    try:
        p.Parse(xmlContent)
    except:
        print "Error: the file " + fname + " is not well-formed"
    f.close()

#
#  Graph class
#
###############################################################################

class callgraph:
    def __init__(self, stack_size_max=12):
        self.g = Graph() 
        self.g.add_node("ROOT")
        self.stack_size_max = stack_size_max

    def addCallStack(self, callstack, leakedbytes):
        global undefined
        # addind "level 0" to the call stack
        lvl = 0
        callstack.insert(0, "ROOT")
        for call in callstack:
            if lvl > self.stack_size_max: 
                break
            if call=="ROOT":
                continue

            # try to find if the call exists already in the callgraph
            if not self.g.has_node(call):
                self.g.add_node(call)
                self.g.add_arrow(callstack[lvl],call)
                self.g.get_arrow(callstack[lvl],call).add_attr("leak", leakedbytes)
                # color leave and uncolor source
                self.g.get_node(call).add_attr("color", "lightblue")
                self.g.get_node(callstack[lvl]).def_attr("color", "none")
            elif not self.g.has_arrow(callstack[lvl], call):
                # check if it's a recursive function
                self.g.add_arrow(callstack[lvl],call)
                self.g.get_arrow(callstack[lvl],call).add_attr("leak", leakedbytes)
                # uncolor source
                self.g.get_node(callstack[lvl]).def_attr("color", "none")
            else:
                # change the weight of the edge (num of leaked bytes)
                arrow = self.g.get_arrow(callstack[lvl],call)
                leaked = arrow.get_attr("leak") 
                arrow.set_attr("leak", leaked + leakedbytes)
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

    def diff_only(self, old_graph, ratio):
        # remove all unchanged arrows (or arrow with lower weight)
        for old_arrow in old_graph.g.get_arrows():
            src_name = old_arrow.get_src_node().get_name()
            dst_name = old_arrow.get_dst_node().get_name()
            old_weight = old_arrow.get_attr("leak")

            new_arrow = self.g.get_arrow(src_name, dst_name)
            if new_arrow is None:
                continue

            new_weight = new_arrow.get_attr("leak")
            if new_weight  <= old_weight * ratio:
                self.g.del_arrow(src_name, dst_name)
            else:
                print "NOT removing arrow between " + src_name + " and " + dst_name + " : " , new_weight , ", " , old_weight

        # remove all node that aren't link to an arrow anymore
        # we can not remove element from a list while looping on it 
        nodes_to_be_removed = [n for n in self.g.get_nodes() if not n.has_arrows()]
        for node in nodes_to_be_removed:
            self.g.del_node( node.get_name() )

    def draw(self, fname="leak.dot", node="ROOT"):
        global results
        # create dot file
        e = ValgrindDOTExporter(self.g)
        e.add_attr("rankdir", "LR") # add attribute to the exporter
        if( results.output_dir ):
            e.export( results.output_dir + "/" + fname + ".dot", fname)
        else:
            e.export(fname + ".dot", fname)


#
#  arg parsing 
#
###############################################################################




import argparse
parser = argparse.ArgumentParser()
#parser.add_argument('-d', action='store_true', default=False,
#                    dest='demangle',
#                    help='demangle symbols')
parser.add_argument('-f', action="store", dest="files", nargs='+', help='Valgrind xml output files', required=True)
parser.add_argument('--diff', action="store", dest="difffiles", nargs='+', help='old Valgrind output files')
parser.add_argument('-finfo', action='store_true', default=False,
                    dest='finfo',
                    help='write file name and line numbers')
parser.add_argument('-s', action='store_false', default=False,
                    dest='single',
                    help='build a single graph with all errors categories')
parser.add_argument('-depth', action='store', dest='depth', type=int,
                    default=12, help='Depth of the graph')
parser.add_argument('-t', action='store', dest='truncate', type=int,
                    default=50, help='Max length of symbols')
parser.add_argument('-o', '--output-dir', action='store', dest='output_dir',
                    help='change output directory')
parser.add_argument('--diff-only', action='store_true', default=False,
                    dest='diffonly', help='write file name and line numbers')
parser.add_argument('--diff-ratio', action='store', dest='ratio', type=float,
                    default=1, help='only display leaks that have increased by at least <ratio> times')
results = parser.parse_args()

# values to set
demangle=False
#demangle=results.demangle      # demangle functions name
writeFileName=results.finfo    # write with the function name the filename and line
depthMax=results.depth         # max depth of the graph (and the call stacks)
truncateVal=results.truncate   # value to truncate function names to
separate_kinds= not results.single # separate the different kind of errors in different graphs
valfiles=results.files


#
#  Main
#
###############################################################################

# g is a list of [name, graph]
if separate_kinds:
    g = []
else:
    g = callgraph()

# if diff required, import diff files
if results.difffiles:
    for f in results.difffiles: 
        importXmlFile(f)   

    # move g to gdiff
    gdiff = g
    if separate_kinds:
        g = []
    else:
        g = callgraph()

    # reinit default values
    leakedbytes = "0"  # init that value
    in_leakedbytes = False
    kind = ""
    in_kind = False
    undefined=1

# add all leaks to the graph
for f in valfiles: 
    importXmlFile(f)

# if diff required, apply diff
if results.difffiles:
    if separate_kinds:
        for graph in g:
            for dgraph in gdiff:
                if graph[0] == dgraph[0]: # compare kinds
                    if results.diffonly:
                        graph[1].diff_only(dgraph[1],results.ratio)
                    else:
                        graph[1].diff(dgraph[1])
    else:
        if results.diffonly:
            g.diff_only(gdiff,results.ratio) 
        else:
            g.diff(gdiff) 

# print the graph
if separate_kinds:
    for graph in g:
        graph[1].draw(graph[0])
else:
    g.draw("graph.dot")
