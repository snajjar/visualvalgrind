#!/usr/bin/env python
import os
import sys
import string

# Import pygraph
from importer.XMLParser import * 



#
#  command calls
#
##############################################################################

def init_g():
    global g, args
    g = []
    XMLParser.xmlparse = XMLParser(args, g)


def add_files(files):
    for f in files: 
        importXmlFile(f)

def print_graph(g):
    for graph in g:
        # print if it has nodes (except ROOT)
        if args.demangle:
            graph[1].demangle()
        if len(graph[1].g.nodes) > 1:
            graph[1].draw(graph[0])

def build_cmd(args):
    global g
    init_g()
    add_files(args.files)
    print_graph(g)


def diff_cmd(args):
    global g
    # import old graphs 
    init_g()
    add_files(args.difffiles)
    g_old = g

    # import new graphs
    init_g()
    add_files(args.files)
    g_new = g

    # init result graph 
    init_g()

    for graph in g_new:
        for dgraph in g_old:
            if graph[0] == dgraph[0]: # compare kinds
                if args.diffonly:
                    graph[1].diff_only(dgraph[1])
                    print_graph(g_new)
                elif args.ratio != 0:
                    diff_graph = graph[1].diff_ratio(dgraph[1],args.ratio)
                    g.append( [graph[0], diff_graph] )
                    print_graph(g)
                else:
                    graph[1].diff(dgraph[1])
                    print_graph(g_new)

#
#  arg parsing 
#
###############################################################################


import argparse
parser = argparse.ArgumentParser(prog='visualvalgrind')
# common arguments
parser.add_argument('-finfo', action='store_true', default=False,
        dest='finfo',
        help='write file name and line numbers')
parser.add_argument('-depth', action='store', dest='depth', type=int,
        default=12, help='maximal depth of the graph')
parser.add_argument('-t', action='store', dest='truncate', type=int,
        default=50, help='maximal length of symbols')
parser.add_argument('-o', '--output-dir', action='store', dest='output_dir',
        help='change output directory')
parser.add_argument('-d', action='store_true', default=False,
        dest='demangle',
        help='demangle symbols')
parser.add_argument('-svg', action='store_true', default=False,
        dest='svg',
        help='output files in SVG format instead of DOT')
subparsers = parser.add_subparsers(help='sub-command help')

#sub-command "build"
parser_build = subparsers.add_parser('build', help='build help')
parser_build.add_argument("files", nargs='+', help='Valgrind xml output files')
parser_build.set_defaults(func=build_cmd)

#sub-command "diff"
parser_diff = subparsers.add_parser('diff', help='diff help')
parser_diff.add_argument('-new', action="store", dest="files", nargs='+', help='new Valgrind output files', required=True)
parser_diff.add_argument('-old', action="store", dest="difffiles", nargs='+', help='old Valgrind output files', required=True)

# -i and -r are exclusive
diff_mode = parser_diff.add_mutually_exclusive_group()
diff_mode.add_argument('-i', action='store_true', default=False,
        dest='diffonly', help='only display leaks that have increased')
diff_mode.add_argument('-r', action='store', dest='ratio', type=float,
        default=0, help='only display leaks that have increased by at least <ratio> times')
parser_diff.set_defaults(func=diff_cmd)


args = parser.parse_args()

if args.output_dir:
    args.output_dir = unicode(args.output_dir, sys.stdin.encoding) 


#
#  MAIN
#
###############################################################################

args.func(args)

