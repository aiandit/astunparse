import ast

from .unparser import Unparser

def isgeneric(x):
    return isinstance(x, str)or isinstance(x, bytes) or isinstance(x, tuple) or isinstance(x, list) \
        or isinstance(x, bool) or isinstance(x, int) or isinstance(x, float) or isinstance(x, complex) \
        or x is None or x is Ellipsis

class ASTNode:
    def clone(self):
        res = ASTNode()
        print('vars', vars(self))
        for i in vars(self):
            field = getattr(self, i)
            if isinstance(field, ASTNode):
                field = field.clone()
            setattr(res, i, field)
        return res

    def __str__(self):
        from . import unparse
        return unparse(self)

    def __repr__(self):
        from . import unparse2j
        return unparse2j(self)

class BinOp(ASTNode):
    _class = 'BinOp'
    op = ""
    left = None
    right = None

    def __init__(self, op):
        self.op = op

class Constant(ASTNode):
    _class = 'Constant'
    value = ""
    kind = ""

    def __init__(self, n):
        self.value = n

class ASTBuilderDict:
    def __init__(self):
        pass

    def __call__(self, tree):
        result = self.dispatch(tree)
        return result

    def dispatch(self, tree):
        if type(tree) == type({}):
            res = ASTNode()
            for key in tree:
                setattr(res, key, self.dispatch(tree[key]))
            if "_class" in tree:
                if tree["_class"] == "NoneType":
                    res = None
                elif tree["_class"] == "EllipsisType":
                    res = Ellipsis
                elif tree["_class"] == "bool":
                    res = True if tree["value"] == "True" else False
                elif tree["_class"] == "bytes":
                    res = ast.literal_eval(tree["value"])
                elif tree["_class"] == "float":
                    if isinstance(tree["value"], str):
                        res = 1e310
                    else:
                        res = tree["value"]
                elif tree["_class"] == "complex":
                    res = complex(res.real, res.imag)
        elif type(tree) == type([]):
            res = list(map(self.dispatch, tree))
        else:
            res = tree
        return res

class ASTBuilderAttr:
    def __init__(self):
        pass

    def __call__(self, tree):
        result = self.dispatch(tree)
        return result

    def dispatch(self, tree):
        if type(tree) == type([]):
            res = list(map(self.dispatch, tree))
        elif isgeneric(tree):
            res = tree
        elif isinstance(tree, object):
            res = ASTNode()
            setattr(res, "_class", tree.__class__.__name__)
            keys = []
            try:
                keys = vars(tree).keys()
            except:
                try:
                    keys = tree.__slots__.keys()
                except:
                    pass
            for key in keys:
                setattr(res, key, self.dispatch(getattr(tree, key)))
        else:
            res = tree
        return res

def resolveop(op):
    if not isinstance(op, str):
        op = Unparser.allops[op._class]
    return op

class ASTNormalizer:
    def __init__(self):
        pass

    def __call__(self, tree):
        result = self.dispatch(tree)
        return result

    def dispatch(self, tree):
        if type(tree) == type([]):
            res = list(map(self.dispatch, tree))
        elif isinstance(tree, ASTNode):
            if tree._class == 'BinOp' or tree._class == 'UnaryOp' or tree._class == 'BoolOp' or tree._class == 'AugAssign':
                tree.op = resolveop(tree.op)
            elif tree._class == 'Compare':
                tree.ops = [resolveop(o) for o in tree.ops]
            for k in vars(tree).keys():
                setattr(tree, k, self.dispatch(getattr(tree, k)))
            res = tree
        else:
            res = tree
        return res

def loadastpy_raw(source, fname="", mode="exec"):
    tree = compile(source, fname, mode, ast.PyCF_ONLY_AST, dont_inherit=True)
    return tree

def loadastobj(tree, fname=""):
    jtree = ASTBuilderAttr()(tree)
    return jtree

def loadastdict(tree, fname=""):
    jtree = ASTBuilderDict()(tree)
    return jtree

def normalize(tree, **kw):
    an = ASTNormalizer()
    return an(tree)

def loadastpy(source, fname="", mode="exec", **kw):
    tree = loadastpy_raw(source, fname=fname, mode=mode)
    jtree = normalize(loadastobj(tree))
    return jtree
