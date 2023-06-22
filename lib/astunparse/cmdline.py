import sys, os, argparse

from . import *

def unparse2jrun():
    run(lambda x, y, **kw: unparse2j(loadast(x, filename=y, **kw), **kw),
        prog="py2json", description="Convert Python code to JSON")

def unparse2xrun():
    run(lambda x, y, **kw: unparse2x(loadast(x, filename=y, **kw), **kw),
        prog="py2xml", description="Convert Python code to XML")

def loadastjrun():
    run(lambda x, y, **kw: unparse(loadastj(x, filename=y)),
        prog="json2py", description="Convert JSON to Python code")

def loadastxrun():
    run(lambda x, y, **kw: unparse(loadastx(x, filename=y)),
        prog="xml2py", description="Convert XML to Python code")

def json2xmlrun():
    run(lambda x, y, **kw: json2xml(x, filename=y, **kw),
        prog="xml2json", description="Convert JSON to XML")

def xml2jsonrun():
    run(lambda x, y, **kw: xml2json(x, filename=y, **kw),
        prog="xml2json", description="Convert XML to JSON")

def py2json2xmlrun():
    unparsel = lambda x, y, **kw: unparse(x)
    run([loadastpy, unparse2j, json2xml, xml2json, loadastj, unparsel],
        prog='py2json2xml', description='Roundtrip to JSON, XML and back. Set -g to dump stages.')

def run(parsefun, prog, description='What the program does'):
    parser = argparse.ArgumentParser(
                    prog=prog,
                    description=description)
    parser.add_argument('filename', nargs='?')
    parser.add_argument('-i', '--indent', type=int, const=1, nargs='?')
    parser.add_argument('-o', '--output', type=str,
                        help='Write output to file')
    parser.add_argument('-g', '--debug', type=str, nargs='?', const='x',
                        help='Keep line number information')
    parser.add_argument('-v', '--verbose',
                        action='store_true')

    args = parser.parse_args()

    input = ''
    if not args.filename:
        input = sys.stdin.read()
        fname = 'stdin'
    else:
        fname = args.filename
        input = open(args.filename).read()
    out = sys.stdout
    if args.output:
        out = open(args.output, 'w')
    debug = True if args.debug else False
    indent = args.indent

    if isinstance(parsefun, list):
        res = ''
        for i, pfun in enumerate(parsefun):
            res = pfun(input, fname, indent=indent, debug=debug)
            if debug:
                if isinstance(res, str):
                    with open(fname + '.' + f'{i}', 'w') as f:
                        f.write(res)
            input = res
        print(res, file=out)
    else:
        print(parsefun(input, fname, indent=indent, debug=debug), file=out)
