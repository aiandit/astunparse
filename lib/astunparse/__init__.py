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
from .json2xml import xml2json, json2xml


__version__ = '1.6.3'


def unparse(tree):
    v = cStringIO()
    Unparser(tree, file=v)
    return v.getvalue()

def dump(tree):
    v = cStringIO()
    Printer(file=v).visit(tree)
    return v.getvalue()

def unparse2j(tree, indent=0, abbrev_none_is_ok_in_fields=None):
    jbuf = cStringIO()
    up1 = Unparser2J(jbuf)
    up1.indent = indent
    if abbrev_none_is_ok_in_fields is not None:
        up1.abbrev_none_is_ok_in_fields = abbrev_none_is_ok_in_fields
    res = up1(tree)
    return jbuf.getvalue()

def unparse2jrun():
    run(lambda x, y: unparse2j(loadast(x, y), indent=1))

def unparse2x(tree, indent=0):
    return json2xml(unparse2j(tree, abbrev_none_is_ok_in_fields=[]), indent=indent)

def unparse2xrun():
    run(lambda x, y: unparse2x(loadast(x, filename=y), indent=1))

def loadastj(jstr, filename='internal.json'):
    jdict = {}
    try:
        jdict = json.loads(jstr)
    except BaseException as ex:
        print('Failed to load JSON: ', ex)
        print(jstr)
        raise(ex)
    return loadastdict(jdict)

def loadastjrun():
    run(lambda x, y: unparse(loadastj(x, filename=y)))

def loadastx(xstr, filename='internal.xml'):
    jstr = ''
    try:
        jstr = xml2json(xstr)
    except BaseException as ex:
        print('Failed to load XML')
        print(xstr)
        raise(ex)
    return loadastj(jstr)

def loadastxrun():
    run(lambda x, y: unparse(loadastx(x, y)))

def json2xmlrun():
    run(lambda x, y: json2xml(x, filename=y, indent=1))

def xml2jsonrun():
    run(lambda x, y: xml2json(x, filename=y, indent=1))

def py2json2xmlrun():
    run([loadastpy, unparse2j, json2xml, xml2json, loadastj, unparse])

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

def run(parsefun):
    import sys, os
    input = ''
    if len(sys.argv) == 1:
        input = sys.stdin.read()
        fname = 'stdin'
    else:
        fname = sys.argv[1]
        input = open(fname).read()
    if isinstance(parsefun, list):
        res = ''
        for i, pfun in enumerate(parsefun):
            res = pfun(input)
            print(pfun, res)
            if os.getenv('DEBUGAST'):
                if isinstance(res, str):
                    with open(fname + '.' + f'{i}', 'w') as f:
                        f.write(res)
            input = res
        print(res)
    else:
        print(parsefun(input, fname))
