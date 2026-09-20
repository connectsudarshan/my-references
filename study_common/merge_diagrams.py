#!/usr/bin/env python3
"""Merge a topic's diagrams_*.js part files into diagrams.js.  usage: python3 merge_diagrams.py <topic_dir>"""
import sys, glob, os
d = os.path.abspath(sys.argv[1])
out = 'var DIAGRAMS={};\n'
for p in sorted(glob.glob(os.path.join(d, 'diagrams_*.js'))):
    out += open(p, encoding='utf-8').read().split('\n', 1)[1]
open(os.path.join(d, 'diagrams.js'), 'w', encoding='utf-8').write(out)
print('merged into', os.path.join(d, 'diagrams.js'))
