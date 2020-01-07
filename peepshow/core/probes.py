import inspect
from collections import OrderedDict
from peepshow.utils.python import id_to_str, hash_to_str
from peepshow.utils.traceback import FrameSummary

def is_bound(obj):
    try:
        return hasattr(obj, '__self__')
    except Exception:
        return False

def is_subscribable(obj):
    try:
        return is_bound(obj.__getitem__)
    except Exception:
        return False

def is_iterable(obj):
    try:
        return is_bound(obj.__iter__)
    except Exception:
        return False

is_callable = lambda obj: callable(obj)

builtin_types = (
type,
type(Ellipsis),
type(None),
bool,
str,
int, float, complex,
list, tuple, set, dict, frozenset,
range, slice,
bytes, bytearray, memoryview)

def is_of_builtin_type(obj):
    for t in builtin_types:
        if isinstance(obj, t):
            return True, t, t.__name__
    return False, None, ''

def can_be_called_wo_args(func):
    if not is_callable(func):
        return False
    try:
        spec = inspect.getfullargspec(func)
    except:
        return False

    len_ = lambda x: 0 if x is None else len(x)

    return len(spec.args) <= len_(spec.defaults) + int(is_bound(func)) and \
           len(spec.kwonlyargs) == len_(spec.kwonlydefaults)

class Feature:
    def __init__(self, value, exists):
        self.value = value
        self.exists = exists

    def __str__(self):
        if self.exists:
            return str(self.value)
        else:
            return 'N/A'

def get_default_action(obj):
    type_is_builtin, type_, _ = is_of_builtin_type(obj)

    if type_is_builtin:
        if issubclass(type_, dict):
            return '**'
        if issubclass(type_, (list, tuple, set, dict, frozenset)):
            return '*'
        if issubclass(type_, type):
            return 'd'        
        return 'pp'
    if isinstance(obj, FrameSummary):
        return '??'
    if is_iterable(obj):
        return '*'
    if can_be_called_wo_args(obj):
        return '()'
    return 'd'


def read_features(obj, feat_list):
    def try_read(feat):
        try:
            value = feat(obj)
            exists = True
        except Exception:
            value = None
            exists = False
        return Feature(value, exists)

    return OrderedDict( (feat[0], try_read(feat[1])) for feat in feat_list )


class Text:
    def __init__(self, text, *, hlight):
        self.text = text
        self.hlight = hlight

    def __str__(self):
        return self.text

    def __bool__(self):
        return self.hlight

def str_vs_repr(obj):
    str_obj = str(obj)
    if obj.__repr__ is obj.__str__:
        return Text('is REPR', hlight=False)
    elif str_obj == repr(obj):
        return Text('REPR', hlight=False)
    else:
        return Text(repr(str_obj), hlight=True)

def qualname_vs_name(obj):
    if obj.__qualname__ == obj.__name__:
        return Text('NAME', hlight=False)
    else:
        return Text(repr(obj.__qualname__), hlight=True)


class HexInt:
    def __init__(self, x):
        self.x = int(x)

    def __str__(self):
        return str(self.x) + ' = ' + hex(self.x)


MAJOR_FEATURES = [
        ('TYPE',          type),
        ('REPR',          lambda obj: repr(repr(obj)) ),
        ('STR',           str_vs_repr),
        ('NAME',          lambda obj: repr(obj.__name__)),
        ('QUALNAME',      qualname_vs_name),
        ('SIGNATURE',     inspect.signature),
        ('CALLABLE',      is_callable),
        ('ITERABLE',      is_iterable),
        ('SUBSCRIBABLE',  is_subscribable),
        ('LEN',           len),
        ('BOOL',          bool),
        ('INT',           HexInt),
        ('ID',            lambda obj: Text(id_to_str(id(obj)), hlight=False)),
        ('HASH',          lambda obj: Text(hash_to_str(hash(obj)), hlight=False)),
        ('BINDING',       lambda obj: obj.__self__),
        ('BASES',         lambda obj: Text(str(obj.__bases__), hlight=False)),
        ('MRO',           lambda obj: Text(str(obj.mro()), hlight=False)),
    ]

MINOR_FEATURES = [
        ('IsModule',            inspect.ismodule),
        ('IsClass',             inspect.isclass),
        ('IsMethod',            inspect.ismethod),
        ('IsFunction',          inspect.isfunction),
        ('IsGeneratorFunction', inspect.isgeneratorfunction),
        ('IsGenerator',         inspect.isgenerator),
        ('IsCoroutineFunction', inspect.iscoroutinefunction),
        ('IsCoroutine',         inspect.iscoroutine),
        ('IsAwaitable',         inspect.isawaitable),
        ('IsAsyncGenFunction',  inspect.isasyncgenfunction),
        ('IsAsyncGen',          inspect.isasyncgen),
        ('IsTraceback',         inspect.istraceback),
        ('IsFrame',             inspect.isframe),
        ('IsCode',              inspect.iscode),
        ('IsBuiltIn',           inspect.isbuiltin),
        ('IsRoutine',           inspect.isroutine),
        ('IsAbstract',          inspect.isabstract),
        ('IsMethodDescriptor',  inspect.ismethoddescriptor),
        ('IsDataDescriptor',    inspect.isdatadescriptor),
        ('IsGetSetDescriptor',  inspect.isgetsetdescriptor),
        ('IsMemberDescriptor',  inspect.ismemberdescriptor),
    ]
