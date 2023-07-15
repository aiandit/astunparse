# coding: utf-8
from __future__ import absolute_import
from six.moves import cStringIO
from .unparser import Unparser
from .printer import Printer
from .astnode import ASTBuilderAttr, ASTBuilderDict, ASTNode
from .astnode import loadastpy, loadastpy_raw, loadastobj, loadastdict, normalize


__version__ = '1.6.3'


def unparse(tree):
    v = cStringIO()
    Unparser(tree, file=v)
    return v.getvalue()


def dump(tree):
    v = cStringIO()
    Printer(file=v).visit(tree)
    return v.getvalue()


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
