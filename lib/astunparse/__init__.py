# coding: utf-8
from __future__ import absolute_import
from six.moves import cStringIO
import itertools
import json
from .unparser import Unparser
from .printer import Printer
from .astnode import ASTBuilderAttr, ASTBuilderDict, ASTNode
from .astnode import loadastpy, loadastpy_raw, loadastobj, loadastdict
from .unparser2j import Unparser2J


__version__ = '1.6.3'


def unparse(tree):
    v = cStringIO()
    Unparser(tree, file=v)
    return v.getvalue()

def dump(tree):
    v = cStringIO()
    Printer(file=v).visit(tree)
    return v.getvalue()

def unparse2j(tree):
    jbuf = cStringIO()
    up1 = Unparser2J(jbuf)
    res = up1(tree)
    return jbuf.getvalue()

def unparse2jrun():
    import sys
    fname = sys.argv[1]
    print(unparse2j(loadast(open(fname).read(), fname)))

def loadastj(jstr, filename='internal.json'):
    jdict = {}
    try:
        jdict = json.loads(jstr)
    except BaseException as ex:
        print('Failed to load JSON')
        print(jstr)
        raise(ex)
    return loadastdict(jdict)

def loadastjrun():
    import sys
    if len(sys.argv) == 1:
        print(unparse(loadastj(sys.stdin.read(), 'stdin')))
    else:
        fname = sys.argv[1]
        ast1 = loadastj(open(fname).read(), fname)
        print(unparse(ast1))

def loadast(source, filename='test.py'):
    if isinstance(source, str):
        firstChar = source[sum(1 for _ in itertools.takewhile(str.isspace,source))]
        if firstChar == '<':
            return loadastx(source, filename)
        elif firstChar == '{':
            return loadastj(source, filename)
        else:
            return loadastpy(source, filename)
    elif isinstance(source, list) or isinstance(source, dict):
        return loadastdict(source, filename)
    else:
        return loadastobj(source, filename)
