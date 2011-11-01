import xml.parsers.expat
import string
import re

from callgraph.Callgraph import * 

#
#  parsing from xml file
#
###############################################################################

class XMLParser:
    def __init__(self, args, g):
        self.leakedbytes = "0"  # init that value
        self.in_leakedbytes = False
        self.kind = ""
        self.in_kind = False
        self.undefined=1
        self.args = args
        self.g = g

        # first round to init variabled
        self.begin_stack()
        self.begin_call()
        self.end_call()
        self.end_stack()

        global xmlparse
        xmlparse = self

    # build graph name and attributes
    def compute_node_name_attr(self, func):
        shape = "note"
        fontsize = "9"
        font = ""
        fname = func[0]
        ffile = func[3]
        fline = func[2]

        # don't loose track of undefined function, make them have a different name
        if fname=="":
            fname="<undefined "+str(self.undefined)+">"
            self.undefined += 1

        # if user wants file and line number, give it to him
        if self.args.finfo:
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
    def process_callstack(self,cs):
        if self.kind=="":
            return

        # search if the kind exists and if so, add to the graph
        for graph in self.g:
            if graph[0] == cs.kind:
                graph[1].addCallstack(cs)
                return

        # if the kind doesn't exist yet, create it
        graph = Callgraph(self.args) 
        graph.addCallstack(cs)
        self.g.append( [cs.kind, graph] )

    def begin_stack(self):
        self.in_stack = True 
        self.stack = [] 

    def end_stack(self):
        self.in_stack = False
        # build the call stack and add it to graph
        func_stack = []
        for func in self.stack:
            node_name = self.compute_node_name_attr(func)
            func_stack.append(node_name)
        func_stack.insert(0, "ROOT")
        cs = Callstack(self.kind, func_stack, int(self.leakedbytes))
        self.process_callstack(cs)
        self.stack = []

    def begin_call(self):
        self.in_call = True
        self.call = ['' for i in xrange(4)]

    def end_call(self):
        self.in_call = False
        self.stack.append(self.call)
        self.call = [] 

    def begin_error(self):
        self.in_error = True

    def end_error(self):
        self.in_error = False 
        self.leakedbytes = 0

    def begin_leakedbytes(self):
        self.in_leakedbytes = True

    def end_leakedbytes(self):
        self.in_leakedbytes = False 

    def begin_kind(self):
        self.in_kind = True

    def end_kind(self):
        self.in_kind = False


    def add_call_attribute(self, value):
        if self.parsing=="fn": 
            # demangle the function name
            fn = value.strip(" \r\n")
            if len(fn)>self.args.truncate:
                fn = fn[:self.args.truncate]+".."
            self.call[0]= fn
        if self.parsing=="dir": 
            self.call[1]=value
        if self.parsing=="line": 
            self.call[2]=value
        if self.parsing=="file": 
            self.call[3]=value


    # 3 handlers that are called when parsing xml
    def xml_start_element(self, name, attr):
        self.parsing = name
        if name=="stack":
            self.begin_stack()
        if name=="frame":
            self.begin_call()
        if name=="error":
            self.begin_error()
        if name=="leakedbytes":
            self.begin_leakedbytes()
        if name=="kind":
            self.begin_kind()

    def xml_handle_data(self, data):
        if data=='\n':
            return

        stripped_data = data.strip(" \r\n")
        if self.in_call:
            if stripped_data != "":
                self.add_call_attribute(stripped_data)
        if self.in_leakedbytes:
            self.leakedbytes = stripped_data
        if self.in_kind:
            self.kind = stripped_data

    def xml_end_element(self, name):
        self.parsing = ""
        if name=="stack":
            self.end_stack()
        if name=="frame":
            self.end_call()
        if name=="error":
            self.end_error()
        if name=="leakedbytes":
            self.end_leakedbytes()
        if name=="kind":
            self.end_kind()

#
#   XML Parsing 
#
##############################################################################
def xml_start_element(name, attr):
    global xmlparse
    xmlparse.xml_start_element(name, attr)

def xml_handle_data(data):
    global xmlparse
    xmlparse.xml_handle_data(data)

def xml_end_element(name):
    global xmlparse
    xmlparse.xml_end_element(name)

def importXmlFile(fname):
    # init the parser
    p = xml.parsers.expat.ParserCreate()
    p.StartElementHandler = xml_start_element
    p.EndElementHandler = xml_end_element
    p.CharacterDataHandler = xml_handle_data

    # parse the file 
    f = open(fname)
    xmlContent = f.read()
    xmlContent = re.sub("\&.*;", "", xmlContent) # remove &amp; and stuff like that
    p.Parse(xmlContent)
    try:
        None
    except:
        print "Error: the file " + fname + " is not well-formed"
    f.close()



