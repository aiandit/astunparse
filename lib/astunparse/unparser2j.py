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
    level = 0
    spacer = ''
    nan = '"NaN"'
    inf = '"Inf"'
    neginf = '"-Inf"'
    none = '""'

    lineinfo_fields = ['end_lineno', 'end_col_offset', 'lineno', 'col_offset']
    astinfo_fields = ['type_comment', 'ctx', 'type_ignores']
    strip_fields = lineinfo_fields
    abbrev_none_is_ok_in_fields = ['annotation', 'asname', 'cause', 'kind', 'kwarg', 'lower', 'returns', 'step', 'type_comment', 'type_ignores', 'vararg']

    def __init__(self, output):
        self.output = output

    def __call__(self, tree):
        self.spacer = ' ' if self.indent > 0 else ''
        return self.dispatch(tree)

    def fill(self, text=''):
        if self.indent:
            self.write('\n' + self.indentstr * self.indent * self.level)
        if text:
            self.write(text)

    def write(self, str):
        self.output.write(str)

    def enter(self):
        self.level += 1

    def leave(self):
        self.level -= 1

    def dispatch(self, tree, name=None):
        if isinstance(tree, list):
            self.fill(f'[')
            for (i,t) in enumerate(tree):
                if i > 0:
                    self.write(f',{self.spacer}')
                self.dispatch(t)
            self.write(f']')
        elif isinstance(tree, ASTNode):
            cname = tree._class
            meth = getattr(self, "_"+cname, None)
            self.write(f'{"{"}"_class":{self.spacer}"{cname}"')
            if meth:
                meth(tree)
            else:
                self.enter()
                fields = [ f for f in vars(tree).keys() if f not in self.strip_fields ]
                for k in fields:
                    if k == '_class': continue
                    elem = getattr(tree, k)
                    self.write(f',')
                    self.fill(f'"{k}":{self.spacer}')
                    self.dispatch(getattr(tree, k), k)
                self.leave()
            self.write(f'{"}"}')
        elif isinstance(tree, bool):
            self.write(f'{"{"}"_class":{self.spacer}"bool",')
            self.fill(f' "value": "{repr(tree)}"{"}"}')
        elif isinstance(tree, int):
            self.write(f'{tree:d}')
        elif isinstance(tree, float):
            if math.isinf(tree):
                self.fill('1e309')
            elif math.isnan(tree):
                self.write(f'{"{"}"_class":{self.spacer}"float",')
                self.fill(f' "value": {self.nan}{"}"}')
            else:
                self.write(f'{tree:f}')
        elif isinstance(tree, complex):
            self.write(f'{"{"}"_class":{self.spacer}"complex",')
            self.fill(f' "real":{self.spacer}')
            self.dispatch(tree.real)
            self.write(',')
            self.fill(f' "imag":{self.spacer}')
            self.dispatch(tree.imag)
            self.write(f'{"}"}')
#        elif isinstance(tree, ellipsis):
#            self.write(f'"..."')
        elif isinstance(tree, str):
            txt = escapejson(tree)
            self.write(f'"{txt}"')
        elif isinstance(tree, bytes):
            self.write(f'{"{"}"_class":{self.spacer}"bytes",')
            self.fill(f' "value": "{repr(tree)}"{"}"}')
        elif tree is Ellipsis:
            self.write(f'{"{"}"_class":{self.spacer}"EllipsisType",')
            self.fill(f' "value": "..."{"}"}')
        elif tree is None:
            if name in self.abbrev_none_is_ok_in_fields:
                self.write('0')
            else:
                self.write(f'{"{"}"_class":{self.spacer}"NoneType"{"}"}')
        else:
            cname = tree.__class__.__name__
            self.write(f'{"{"}"_class":{self.spacer}"{cname}"')
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
                    self.fill(f'"{k}":{self.spacer}')
                    self.dispatch(elem, k)
                self.leave()
            self.write('}')
