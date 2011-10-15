#!/usr/bin/env python
import os
import sys
import string
import xml.parsers.expat
import subprocess

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
        self.f.write(src_name + " -> " + dst_name +
                " [label="+str(arrow.get_attr("leak")) + "]\n")

#
#  parsing from xml file
#
###############################################################################

# init some values
leakedbytes = "0"  # init that value
in_leakedbytes = False
kind = ""
in_kind = False

# build graph name and attributes
def compute_node_name_attr(func):
    global writeFileName
    shape = "note"
    fontsize = "9"
    font = ""
    fname = func[0]
    ffile = func[3]
    fline = func[2]
    if writeFileName:
        label=fname
        if ffile!="" and fline!="":
            label+="\\n"+ffile+":"+fline
        else:
            label = fname
    else:
        label = fname
    return "\"" + label + "\""
    #return "\"" + label + "\"[fontsize=" + fontsize + ",shape=" + shape + "]" 

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
    call = ['' for i in range(4)]

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
    end_stack()
    end_call()

    # parse the file 
    f = open(fname)
    xmlContent = f.read()
    p.Parse(xmlContent)
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
            elif not self.g.has_arrow(callstack[lvl], call):
                # check if it's a recursive function
                self.g.add_arrow(callstack[lvl],call)
                self.g.get_arrow(callstack[lvl],call).add_attr("leak", leakedbytes)
            else:
                # change the weight of the edge (num of leaked bytes)
                arrow = self.g.get_arrow(callstack[lvl],call)
                leaked = arrow.get_attr("leak") 
                print "leaked", leaked
                arrow.set_attr("leak", leaked + leakedbytes)
            lvl += 1

    def draw(self, fname="leak.dot", node="ROOT"):
        # create dot file
        e = ValgrindDOTExporter(self.g)
        e.add_attr("rankdir", "LR") # add attribute to the exporter
        e.export(fname)

#
#  Main
#
###############################################################################

# values to set
demangle=False          # demangle functions name
writeFileName=True      # write with the function name the filename and line
depthMax=12             # max depth of the graph (and the call stacks)
truncateVal=50          # value to truncate function names to
separate_kinds=False    # separate the different kind of errors in different graphs

# g is a list of [name, graph]
if separate_kinds:
    g = []
else:
    g = callgraph()

# add all leaks to the graph
for f in sys.argv[1:]:
    # print "parsing file: " + f
    importXmlFile(f)

# print the graph
if separate_kinds:
    for graph in g:
        # print "printing graph " + graph[0]
        graph[1].draw(graph[0]+ ".dot")
else:
    g.draw("graph.dot")
