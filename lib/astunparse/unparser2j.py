import sys
import os
import inspect
import ast
import json
import math

from .astnode import ASTNode
from .unparser import Unparser

def escapejson(str):
    return str.replace("\\", "\\\\").replace("\n", "\\n").replace("\r", "\\r").replace("\t", "\\t").replace("\"", "\\\"")

class Unparser2J:
    indentstr = ' '
    indent = 0
    nan = '"NaN"'
    inf = '"Inf"'
    neginf = '"-Inf"'
    none = '""'

    lineinfo_fields = ['end_lineno', 'end_col_offset', 'lineno', 'col_offset']
    astinfo_fields = ['type_comment', 'ctx', 'type_ignores']
    strip_fields = lineinfo_fields
    abbrev_none_is_ok_in_fields = ['kwarg', 'kind', 'type_comment', 'asname', 'annotation', 'vararg', 'returns', 'cause', 'lower', 'step']

    def __init__(self, output):
        self.output = output

    def __call__(self, tree):
        return self.dispatch(tree)

    def fill(self, text=''):
        if self.indentstr:
            self.write('\n' + self.indentstr * self.indent)
        if text:
            self.write(text)

    def write(self, str):
        self.output.write(str)

    def setIndent(self, s):
        self.indentstr = s

    def enter(self):
        self.indent += 1

    def leave(self):
        self.indent -= 1

    def dispatch(self, tree, name=None):
        if isinstance(tree, list):
            self.fill(f'[')
            for (i,t) in enumerate(tree):
                if i > 0:
                    self.write(f', ')
                self.dispatch(t)
            self.write(f']')
        elif isinstance(tree, ASTNode):
            cname = tree._class
            meth = getattr(self, "_"+cname, None)
            self.write(f'{"{"}"_class": "{cname}"')
            if meth:
                meth(tree)
            else:
                self.enter()
                fields = [ f for f in vars(tree).keys() if f not in self.strip_fields ]
                for k in fields:
                    if k == '_class': continue
                    elem = getattr(tree, k)
                    self.write(f',')
                    self.fill(f'"{k}": ')
                    self.dispatch(getattr(tree, k), k)
                self.leave()
            self.write(f'{"}"}')
        elif isinstance(tree, bool):
            self.write(f'{"{"}"_class": "bool",')
            self.fill(f' "value": "{repr(tree)}"{"}"}')
        elif isinstance(tree, int):
            self.write(f'{tree:d}')
        elif isinstance(tree, float):
            if math.isinf(tree):
                self.fill('1e309')
            elif math.isnan(tree):
                self.write(f'{"{"}"_class": "float",')
                self.fill(f' "value": {self.nan}{"}"}')
            else:
                self.write(f'{tree:f}')
        elif isinstance(tree, complex):
            self.write(f'{"{"}"_class": "complex",')
            self.fill(f' "real": ')
            self.dispatch(tree.real)
            self.write(',')
            self.fill(f' "imag": ')
            self.dispatch(tree.imag)
            self.write(f'{"}"}')
#        elif isinstance(tree, ellipsis):
#            self.write(f'"..."')
        elif isinstance(tree, str):
            txt = escapejson(tree)
            self.write(f'"{txt}"')
        elif isinstance(tree, bytes):
            self.write(f'{"{"}"_class": "bytes",')
            self.fill(f' "value": "{repr(tree)}"{"}"}')
        elif tree is Ellipsis:
            self.write(f'{"{"}"_class": "EllipsisType",')
            self.fill(f' "value": "..."{"}"}')
        elif tree is None:
            if name in self.abbrev_none_is_ok_in_fields:
                self.write('0')
            else:
                self.write(f'{"{"}"_class": "NoneType"{"}"}')
        else:
            cname = tree.__class__.__name__
            self.write(f'{"{"}"_class": "{cname}"')
            meth = getattr(self, "_"+cname, None)
            if meth:
                meth(tree)
            else:
                self.enter()
                fieldnames = {}
                try:
                    fieldnames = vars(tree)
                except BaseException as ex:
                    print(f'type {type(tree)} does not have dict!')
                    print(tree)
                    print(ex)
                    pass
                fields = [ f for f in fieldnames if f not in self.strip_fields ]
                for k in fields:
                    elem = getattr(tree, k)
                    self.write(f',')
                    self.fill(f'"{k}": ')
                    self.dispatch(elem, k)
                self.leave()
            self.write('}')

    def __BinOp(self, t):
        self.write(f',')
        self.enter()
        self.fill(f'"left": ')
        self.dispatch(t.left)
        if isinstance(t.op, str):
            op = t.op
        else:
            cname = t.op.__class__.__name__
            op = Unparser.binop[cname]
        self.fill(f', "op": "{op}",')
        self.fill(f'"right": ')
        self.dispatch(t.right)
        self.leave()
