import sys, os, argparse

from . import *

from . import __version__

unparsel = lambda x, y, **kw: unparse(x)

infos = dict(
    py2py=dict(func=lambda x, y, **kw: unparse(loadastpy(x, filename=y, **kw), **kw),
               desc="Load Python code and pretty-print")
    , pydump=dict(func=lambda x, y, **kw: ast_dump(loadastpy_raw(x, filename=y), **kw),
                  desc="Load Python code and dump tree in text form")
    , py2json=dict(func=lambda x, y, **kw: unparse2j(loadastpy(x, filename=y, **kw), **kw),
                   desc="Convert Python code to JSON")
    , py2xml=dict(func=lambda x, y, **kw: unparse2x(loadastpy(x, filename=y, **kw), **kw),
                  desc="Convert Python code to XML")
    , json2py=dict(func=lambda x, y, **kw: unparse(loadastj(x, filename=y)),
                   desc="Convert JSON to Python code")
    , xml2py=dict(func=lambda x, y, **kw: unparse(loadastx(x, filename=y)),
                  desc="Convert XML to Python code")
    , json2xml=dict(func=lambda x, y, **kw: json2xml(x, filename=y, **kw),
                    desc="Convert JSON to XML")
    , xml2json=dict(func=lambda x, y, **kw: xml2json(x, filename=y, **kw),
                    desc="Convert XML to JSON")
    , py2json2xml=dict(func=[loadastpy, unparse2j, json2xml, xml2json, loadastj, unparsel],
                       desc="Roundtrip to JSON, XML and back. Set -g to dump stages.")
)

def unparse2pyrun():
    run(prog="py2py")

def pydumprun():
    run(prog="pydump")

def unparse2jrun():
    run(prog="py2json")

def unparse2xrun():
    run(prog="py2xml")

def loadastjrun():
    run(prog="json2py")

def loadastxrun():
    run(prog="xml2py")

def json2xmlrun():
    run(prog="xml2json")

def xml2jsonrun():
    run(prog="xml2json")

def py2json2xmlrun():
    run(prog='py2json2xml')

def getparser(prog, description='What the program does', parser=None):
    if parser is None:
        parser = argparse.ArgumentParser(
            prog=prog,
            description=description)
    parser.add_argument('filename', nargs='?')
    parser.add_argument('-e', '--show-empty', action='store_true')
    parser.add_argument('-f', '--annotate-fields', action='store_true')
    parser.add_argument('-i', '--indent', type=int, const=1, nargs='?',
                        metavar='N', help='Indent output with N spaces')
    parser.add_argument('-o', '--output', type=str, metavar='FILE',
                        help='Write output to FILE')
    parser.add_argument('-g', '--debug', action='store_true',
                        help='Keep line number information')
    version = __version__
    parser.add_argument('-v', '--version', action='version', version=f'{prog} {version}')

    return parser

def run(prog):
    info = infos[prog]
    parser = getparser(prog=prog, description=info['desc'])
    args = parser.parse_args()
    parsefun=info['func']
    processargs(args, parsefun)

def processargs(args, parsefun):

    input = ''
    if not args.filename or args.filename == '-':
        input = sys.stdin.read()
        fname = 'stdin'
    else:
        fname = args.filename
        input = open(args.filename).read()
    out = sys.stdout
    if args.output:
        out = open(args.output, 'w')
    debug = True if args.debug else False

    pfkw = { k: v for k,v in vars(args).items() if k != 'filename' }
    if 'debug' in pfkw:
        pfkw['include_attributes'] = pfkw['debug']


    if isinstance(parsefun, list):
        res = ''
        for i, pfun in enumerate(parsefun):
            res = pfun(input, fname, **pfkw)
            if debug:
                if isinstance(res, str):
                    with open(fname + '.' + f'{i}', 'w') as f:
                        f.write(res)
            input = res
        print(res, file=out)
    else:
        print(parsefun(input, fname, **pfkw), file=out)
