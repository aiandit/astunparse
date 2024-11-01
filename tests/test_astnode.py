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
        # check Python code is identical
        if astunparse.unparse(ast1) != astunparse.unparse(ast2):
            print('Fail', astunparse.unparse(ast1), astunparse.unparse(ast2))
        self.assertEqual(astunparse.unparse(ast1), astunparse.unparse(ast2))

    def check_roundtrip(self, code1, filename="internal", mode="exec"):
        # test roundtrip to ASTNode tree structure
        ast1 = astunparse.loadastpy(str(code1), filename, mode)
        code2 = astunparse.unparse(ast1)
        ast2 = compile(code2, filename, mode, ast.PyCF_ONLY_AST)
        self.assertASTEqual(ast1, ast2)

    def test_clone(self):
        code = """
def f(x):
   r = x*x"""
        ast1 = astunparse.loadastpy(code)
        ast2 = ast1.clone()
        astunparse.unparse(ast2)
