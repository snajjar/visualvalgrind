#!/usr/bin/env python
import os
import sys
import string
import xml.parsers.expat
import subprocess

# Import graphviz
import sys
sys.path.append('..')
sys.path.append('/usr/lib/graphviz/python/')
sys.path.append('/usr/lib64/graphviz/python/')
#import gv

# Import pygraph
from pygraph.classes.graph import graph
from pygraph.classes.digraph import digraph
from pygraph.algorithms.searching import breadth_first_search
from pygraph.readwrite.dot import write

# raise that exception in case of parsing error
class EndParsingError(Exception):
	pass

#
#  parsing from suppression file
#
###############################################################################

def readName(file):
	return file.readline().strip(" \r\n")

def readValgrindOption(file):
	return file.readline().strip(" \r\n")

def readValgrindStack(file):
	stack = []
	while 1:
		line = file.readline()
		if not line.find("}"):
			break
		
		line = line.replace("fun:","").replace("obj:*","obj").strip(" \r\n")
		
		# truncate the string
		if len(line)>=32:
			line = line[:30] + ".."

		stack.append(line)
	return stack

def importSuppFile(file):
	while 1:
		line = file.readline()
		if not line:
			raise EndParsingError() 
		
		if not line.find("{"):
			# entering a suppression
			name = readName(file)
			val_option = readValgrindOption(file)
			stack = readValgrindStack(file)
			return stack
		else:
			pass

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
	global g, depthMax

	# search if the kind exists and if so, add to the graph
	for graph in g:
		if graph[0] == kind:
			graph[1].addCallStack(callstack, int(leakedbytes))
			return

	if kind=="":
		return

	# if the kind doesn't exist yet, create it
	graph = callgraph(depthMax) 
	graph.addCallStack(callstack, int(leakedbytes))
	g.append( [kind, graph] )

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
		self.g = digraph() 
		self.g.add_node("ROOT")
		self.stack_size_max = stack_size_max

	def getSpanningTree(self, graph, node):
		st, order = breadth_first_search(graph, root=node)
		gst = digraph()
		gst.add_spanning_tree(st)
		return gst

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
				self.g.add_edge((callstack[lvl], call), leakedbytes) 
			elif not self.g.has_edge((callstack[lvl], call)):
				# check if it's a recursive function
				self.g.add_edge((callstack[lvl], call), leakedbytes) 
			else:
				# change the weight of the edge (num of leaked bytes)
				leaked = self.g.edge_weight((callstack[lvl], call))
				self.g.set_edge_weight((callstack[lvl], call), leaked + leakedbytes)
			lvl += 1

	def draw(self, fname="leak.dot", node="ROOT"):
		# get the spanning tree from our graph 
		gst = self.getSpanningTree(self.g, node)

		# the spanning tree doesn't have the weight we set on each edge,
		# so we re-add it manually
		edges = gst.edges()
		for edge in edges:
			weight = self.g.edge_weight(edge)
			gst.set_edge_weight(edge, weight)

		# create dot file
		dotString = write(gst, True)
		f = open(fname, 'w')
		output = dotString.split("\n", 2)
		f.write(output[0] + "\nrankdir=LR\nfontsize=9" + output[2])
		f.close()
		return

	def drawLevelRecursive(self, st, lvl, node):
		if lvl==0:
			# write the file from the node 
			dot = write(self.getSpanningTree(st,node), True)
			self.writeDotFile(node, dot)
			self.writePicFile(node, "jpg")
		else:
			for n in st.neighbors(node):
				self.drawLevelRecursive(st, lvl-1, n)

	def drawLevel(self, lvl=0):
		# create log directory
		try:
			os.system('rm -rf results')
			os.makedirs('results/dot')
			os.makedirs('results/pic')
		except OSError:
			#print "Error creating dirs result/dot and result/pic"
			pass
		# create the spawning tree
		gst = self.getSpanningTree(self.g, "ROOT")
		self.drawLevelRecursive(gst, lvl, "ROOT")

	def write(self, node, lvl):
		# create the spanning tree
		gst = self.getSpanningTree(self.g, node)
		neighbors = gst.neighbors(node)
		tab = ""
		for i in range(lvl):
			tab += "\t"
		print tab + "\--> " + node + "\n"
		for r in neighbors:
			self.write(r, lvl+1)

	def writeDotFile(self, name, dotString):
		f = open('results/dot/' + name + '.dot', 'a')
		output = dotString.split("\n", 2)
		f.write(output[0] + "\nrankdir=LR\nfontsize=9\n" + output[2])
		f.close()

	def writePicFile(self, name, format):
		os.system("dot -T" + format + " results/dot/" + name + 
			".dot > results/pic/" + name + "." + format)


#
#  Main
#
###############################################################################

# values to set
demangle=False			# demangle functions name
writeFileName=True		# write with the function name the filename and line
depthMax=12				# max depth of the graph (and the call stacks)
truncateVal=30			# value to truncate function names to

# g is a list of [name, graph]
g = []

# add all leaks to the graph
for f in sys.argv[1:]:
	# print "parsing file: " + f
	importXmlFile(f)

# print the graph
for graph in g:
	# print "printing graph " + graph[0]
	graph[1].draw(graph[0]+ ".dot")
