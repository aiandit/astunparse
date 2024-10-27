from __future__ import print_function
import sys
import os
import argparse
from .unparser import roundtrip
from . import ast_dump
from . import loadastpy_raw
from . import cmdline
from . import __version__


def roundtrip_recursive(target, dump_tree=False):
    if os.path.isfile(target):
        print(target)
        print("=" * len(target))
        if dump_tree:
            with open(target) as f:
                print(ast_dump(loadastpy_raw(f.read(), filename=target)))
            # not working
            # dump(target)
            # dump(loadastpy_raw(target))
        else:
            roundtrip(target)
        print()
    elif os.path.isdir(target):
        for item in os.listdir(target):
            if item.endswith(".py"):
                roundtrip_recursive(os.path.join(target, item), dump_tree)
    else:
        print(
            "WARNING: skipping '%s', not a file or directory" % target,
            file=sys.stderr
        )


def main(args):
    descr = """astunparse (AI&IT fork) provides an AST representation
of Python code, with JSON and XML I/O"""
    parser = argparse.ArgumentParser(prog="astunparse",
                                     description=descr,
                                     epilog='Visit us on the web: https://ai-and-it.de')

    parser.add_argument('-v', '--verbose', action='version',
                        version=f'astunparse {__version__}')

    subparsers = parser.add_subparsers(help='Subcommands', dest='tool')

    subcmds = ['py2json', 'json2py',
               'py2xml', 'xml2py',
               'xml2json', 'json2xml',
               'py2py', 'pydump',
               'py2json2xml']

    for cmd in subcmds:
        sub_parser = subparsers.add_parser(cmd,
                                           description=cmdline.infos[cmd]['desc'],
                                           help=cmdline.infos[cmd]['desc'])
        sub_parser = cmdline.getparser(prog='astunparse ' + cmd,
                                       parser=sub_parser)

    sub_parser = subparsers.add_parser('default')
    sub_parser.add_argument(
        'target',
        nargs='*',
        help="Files or directories to show roundtripped source for"
    )
    sub_parser.add_argument(
        '--dump',
        type=bool,
        help="Show a pretty-printed AST instead of the source"
    )

    if len(args) and args[0] not in subcmds:
        # backward compat
        args = ['default'] + args
    arguments = parser.parse_args(args)

    if arguments.tool in subcmds:
        cmdline.processargs(arguments, cmdline.infos[arguments.tool]['func'])
    else:
        for target in arguments.target:
            roundtrip_recursive(target, dump_tree=arguments.dump)

def run():
    main(sys.argv[1:])

if __name__ == "__main__":
    run()
