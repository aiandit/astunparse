import ast
import sys
if sys.version_info < (2, 7):
    import unittest2 as unittest
else:
    import unittest

import astunparse
from tests.common import AstunparseCommonTestCase

class UnparseTestCase(AstunparseCommonTestCase, unittest.TestCase):

    def assertASTEqual(self, ast1, ast2):
        self.assertEqual(ast.dump(ast1), ast.dump(ast2))

    def check_roundtrip(self, code1, filename="internal", mode="exec"):
        ast1 = compile(str(code1), filename, mode, ast.PyCF_ONLY_AST)
        code2 = astunparse.unparse(ast1)
        ast2 = compile(code2, filename, mode, ast.PyCF_ONLY_AST)
        self.assertASTEqual(ast1, ast2)

    def visit(self, node, l=0):
        if l > 10:
            return
        unpc = astunparse.unparse(node)
        if isinstance(node, list) or isinstance(node, tuple):
            [self.visit(n, l+1) for n in node]
        elif isinstance(node, object):
            names = [n for n in dir(node) if n[0] != "_"]
            for n in names:
                self.visit(getattr(node, n), l+1)

    def unparse_all_items(self, code1, filename="internal", mode="exec"):
        ast1 = compile(str(code1), filename, mode, ast.PyCF_ONLY_AST)
        self.visit(ast1)
