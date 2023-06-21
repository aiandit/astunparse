import sys
import json
from io import StringIO
import lxml.etree
import os
import math

from .unparser2j import escapejson

INFSTR = '1e309'

class JSON2XMLPrinter:
    input = {}
    output = None
    level = 0
    indent = ' '

    def __init__(self, dict, output=sys.stdout):
        self.input = dict
        self.output = output
        self.write('<?xml version="1.0"?>')
        self.dispatch(dict)

    def fill(self):
        self.output.write('\n' + self.indent * self.level)

    def write(self, str):
        self.output.write(str)

    def welem(self, name, content):
        self.output.write(f'<{name}>{content}</{name}>')

    def wstart(self, name, attrs={}):
        self.fill()
        attrstr = ''
        for a in attrs:
            attrstr += f'{a}="{attrs[a]}"'
        if attrstr:
            attrstr = ' ' + attrstr
        self.output.write(f'<{name}{attrstr}>')
        self.level += 1
    def wend(self, name, fill=True):
        self.level -= 1
        if fill:
            self.fill()
        self.output.write(f'</{name}>')

    def dispatch(self, d, name='dict'):
        if type(d) == type({}):
            cname =  d['_class'] if '_class' in d else None
            self.wstart(name, {'_class': cname} if cname else {})
            for k in d:
                if k == '_class':
                    continue
                self.dispatch(d[k], k)
            self.wend(name)
        elif type(d) == type([]):
            self.wstart(name, {'_class': 'list'})
            for k in d:
                self.dispatch(k)
            self.wend(name)
        elif type(d) == type(0) or type(d) == type(0.0):
            self.wstart(name)
            self.wstart('num')
            if math.isinf(d):
                self.write(f'{INFSTR}')
            else:
                self.write(f'{d}')
            self.wend('num', False)
            self.wend(name)
        elif type(d) == type(''):
            self.wstart(name)
            self.wstart('str')
            self.write(escapejson(d.replace('&', '&amp;').replace('<', '&lt;')))
            self.wend('str', False)
            self.wend(name)
        else:
            self.wstart(name)
            self.write(json.dumps(d))
            self.wend(name, False)

def runXSLT(docstr, xsltfname):
    with open(xsltfname) as f:
        xsltstr = f.read()
    xsltdoc = lxml.etree.fromstring(xsltstr)
    transform = lxml.etree.XSLT(xsltdoc)
    xmldoc = lxml.etree.fromstring(docstr)
    result = transform(xmldoc)
    return str(result)

def xml2json(xmlstr, fname=''):
    return runXSLT(xmlstr, 'xml2json.xsl')

def json2xml(jstr, fname=''):
    jdict = json.loads(jstr)
    output = StringIO()
    JSON2XMLPrinter(jdict, output)
    xstr = output.getvalue()
    return xstr
