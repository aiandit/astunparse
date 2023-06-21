import ast
import sys
import json
if sys.version_info < (2, 7):
    import unittest2 as unittest
else:
    import unittest

import astunparse
from tests.common import AstunparseCommonTestCase

class UnparseTestCase(AstunparseCommonTestCase, unittest.TestCase):

    def assertASTEqual(self, ast1, ast2):
        if astunparse.unparse2x(ast1) != astunparse.unparse2x(ast2):
            print('Fail', astunparse.unparse2x(ast1), astunparse.unparse2x(ast2))
        self.assertEqual(astunparse.unparse2x(ast1), astunparse.unparse2x(ast2))
        if astunparse.unparse(ast1) != astunparse.unparse(ast2):
            print('Fail', astunparse.unparse(ast1), astunparse.unparse(ast2))
        self.assertEqual(astunparse.unparse(ast1), astunparse.unparse(ast2))

    def check_roundtrip(self, code1, filename="internal", mode="exec"):
        ast1 = astunparse.loadastpy(str(code1), filename, mode)
        xstr = astunparse.unparse2x(ast1)
        ast2 = astunparse.loadast(xstr)
        self.assertASTEqual(ast1, ast2)
