import ast
from .unparser import Unparser

# with fastFields == True the code is about twice as fast, but only
# works as long as all fields are set in code (like in __init__ or
# anywhere else, by obj.field= or setattr), and not in the class
# def. The node classes BinOp, Name, etc. follow this rule.
fastFields = True

def fields(x, all=False):
    if fastFields and not all:
        return vars(x)
    else:
        xfields = getattr(x, '__dict__', {})
        cfields = getattr(x.__class__, '__dict__', {})
        return [f for f, v in (cfields | xfields).items() if "__" not in f and not callable(v)]

def isgeneric(x):
    return isinstance(x, str)or isinstance(x, bytes) or isinstance(x, tuple) or isinstance(x, list) \
        or isinstance(x, bool) or isinstance(x, int) or isinstance(x, float) or isinstance(x, complex) \
        or x is None or x is Ellipsis

class ASTNode:
    def clone(self):
        res = ASTNode()
        for i in fields(self):
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
    def __init__(self, op):
        self._class = 'BinOp'
        self.op = op
        self.left = None
        self.right = None

class Constant(ASTNode):
    def __init__(self, n):
        self._class = 'Constant'
        self.kind = ""
        self.value = n

class Name(ASTNode):
    def __init__(self, id):
        self._class = 'Name'
        self.id = id

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
                keys = fields(tree)
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
            for k in fields(tree):
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

def loadastpy(source, fname="", mode="exec", **kw):
    tree = loadastpy_raw(source, fname=fname, mode=mode)
    jtree = normalize(loadastobj(tree))
    return jtree

def normalize(tree, **kw):
    an = ASTNormalizer()
    return an(tree)
