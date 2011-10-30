#!/usr/bin/env python

import os
import sys
sys.path.append(os.path.join(os.getcwd(), "../../../src/core"))
import IOGraph
sys.path.append(os.path.join(os.getcwd(), "../../../src/exporter/DOTExporter"))
from DOTExporter import *

g = IOGraph.Graph()
g.add_node("a")
g.add_node("b")
g.add_node("c")
g.add_node("d")
g.add_arrow("a", "b")
g.add_arrow("b", "c")
g.add_arrow("c", "d")
g.add_arrow("d", "a")
g.add_arrow("b", "d")

e = DOTExporter(g)
e.export("test1.dot")
