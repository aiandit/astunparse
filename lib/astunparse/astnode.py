
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
    return isinstance(x, str) or type(x).__name__ == 'unicode' \
        or isinstance(x, bytes) or isinstance(x, bytearray) \
        or isinstance(x, tuple) or isinstance(x, list) or isinstance(x, dict) \
        or isinstance(x, bool) or isinstance(x, int) or type(x).__name__ == 'long' \
        or isinstance(x, float) or isinstance(x, complex) \
        or x is None or x is Ellipsis

def clone(x):
    if isinstance(x, list):
        res = [clone(f) for f in x]
    elif isinstance(x, tuple):
        res = tuple([clone(f) for f in x])
    elif isinstance(x, dict):
        res = {k: clone(v) for k, v in x.items()}
    elif isinstance(x, ASTNode):
        res = ASTNode()
        for i in fields(x):
            field = getattr(x, i)
            setattr(res, i, clone(field))
    else:
        res = x
    return res

class ASTNode:
    def clone(self):
        return clone(self)

    def __str__(self):
        from . import unparse
        return unparse(self)

    def __repr__(self):
        return "ASTNode[%s]" % (getattr(self, '._class', 'unknown'))

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

def loadastpy_raw(source, filename="", mode="exec"):
    tree = compile(source, filename, mode, ast.PyCF_ONLY_AST, dont_inherit=True)
    return tree

def loadastobj(tree, filename=""):
    jtree = ASTBuilderAttr()(tree)
    return jtree

def loadastdict(tree, filename=""):
    jtree = ASTBuilderDict()(tree)
    return jtree

def loadastpy(source, filename="", mode="exec", **kw):
    tree = loadastpy_raw(source, filename=filename, mode=mode)
    jtree = normalize(loadastobj(tree))
    return jtree

def normalize(tree, **kw):
    an = ASTNormalizer()
    return an(tree)

def ast_dump(rawtree, **kw):
    use = ['indent', 'include_attributes', 'annotate_fields']
    # starting with python 3.13
    # use += ['show_empty']
    dkw = { k: v for k,v in kw.items() if k in use }
    return ast.dump(rawtree, **dkw)
