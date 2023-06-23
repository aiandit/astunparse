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
        # check JSON representation is identical
        if astunparse.unparse2j(ast1, indent=1) != astunparse.unparse2j(ast2, indent=1):
            print('Fail', astunparse.unparse2j(ast1, indent=1), astunparse.unparse2j(ast2, indent=1))
        self.assertEqual(astunparse.unparse2j(ast1, indent=1), astunparse.unparse2j(ast2, indent=1))
        # check Python code is identical
        if astunparse.unparse(ast1) != astunparse.unparse(ast2):
            print('Fail', astunparse.unparse(ast1), astunparse.unparse(ast2))
        self.assertEqual(astunparse.unparse(ast1), astunparse.unparse(ast2))

    def check_roundtrip(self, code1, filename="internal", mode="exec"):
        # test roundtrip to JSON format
        ast1 = astunparse.loadastpy(str(code1), filename, mode)
        jstr = astunparse.unparse2j(ast1)
        ast2 = astunparse.loadast(jstr)
        self.assertASTEqual(ast1, ast2)
        # test same with AST dict structure obtained from loading JSON
        ast2 = astunparse.loadast(json.loads(jstr))
        self.assertASTEqual(ast1, ast2)
        # test same with indented JSON
        jstr = astunparse.unparse2j(ast1,1)
        ast2 = astunparse.loadast(jstr)
        self.assertASTEqual(ast1, ast2)
        # test same with indented JSON, normalized tree
        jstr = astunparse.unparse2j(astunparse.normalize(ast2),1)
        ast2 = astunparse.loadast(jstr)
        self.assertASTEqual(ast1, ast2)
