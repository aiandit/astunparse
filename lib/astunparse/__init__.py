# coding: utf-8
from __future__ import absolute_import
from six.moves import cStringIO
import itertools
import json
from .unparser import Unparser
from .printer import Printer
from .astnode import ASTBuilderAttr, ASTBuilderDict, ASTNode
from .astnode import loadastpy, loadastpy_raw, loadastobj, loadastdict, normalize
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


def unparse2j(tree, filename='internal.py', indent=0, debug=0, abbrev_none_is_ok_in_fields=None, strip_fields=None):
    jbuf = cStringIO()
    up1 = Unparser2J(jbuf)
    up1.indent = indent
    if abbrev_none_is_ok_in_fields is not None:
        up1.abbrev_none_is_ok_in_fields = abbrev_none_is_ok_in_fields
    if debug:
        if isinstance(strip_fields, list):
            up1.strip_fields = strip_fields
        else:
            up1.strip_fields = []
    res = up1(tree)
    return jbuf.getvalue()


def unparse2x(tree, indent=0, debug=0):
    return json2xml(unparse2j(tree, abbrev_none_is_ok_in_fields=[], debug=debug), indent=indent)


def loadastj(jstr, filename='internal.json', **kw):
    jdict = {}
    try:
        jdict = json.loads(jstr)
    except BaseException as ex:
        print('Failed to load JSON: ', ex)
        print(jstr)
        raise(ex)
    return loadastdict(jdict)


def loadastx(xstr, filename='internal.xml'):
    jstr = ''
    try:
        jstr = xml2json(xstr)
    except BaseException as ex:
        print('Failed to load XML')
        print(xstr)
        raise(ex)
    return loadastj(jstr)


def loadast(source, filename='test.py', **kw):
    if isinstance(source, str):
        firstChar = source[sum(1 for _ in itertools.takewhile(str.isspace,source))]
        if firstChar == '<':
            return loadastx(source, filename)
        elif firstChar == '{':
            return loadastj(source, filename)
        else:
            return loadastpy(source, filename, **kw)
    elif isinstance(source, list) or isinstance(source, dict):
        return loadastdict(source, filename)
    else:
        return loadastobj(source, filename)
