import inspect
import ast
import astunparse
import astor
import pprintpp
from peepshow.utils.system import OS_BITS
from textwrap import dedent
from peepshow.core.env import Env
from functools import wraps
from itertools import islice
from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import TerminalFormatter

def always_assert(condition):
    """Assert which works also when code optimization is enabled"""
    if not condition:
        raise AssertionError


def caller_gloloc(level=2):
    """Return globals & locals of the caller of the caller.

    level: 0 is current frame, 1 is the caller, 2 is caller of the caller
    """
    caller_frame_info = inspect.stack()[level]
    caller_frame = caller_frame_info.frame
    glo = caller_frame.f_globals
    loc = caller_frame.f_locals
    return Env(glo, loc)


def arg_names(level=2):
    """Try to determine names of the variables given as arguments to the caller
    of the caller. This works only for trivial function invocations. Otherwise
    either results may be corrupted or exception will be raised.

    level: 0 is current frame, 1 is the caller, 2 is caller of the caller
    """
    try:
        caller_frame_info = inspect.stack()[level]
        caller_context = caller_frame_info.code_context
        code = dedent(''.join(caller_context))
        tree = ast.parse(code, '', 'eval')
        always_assert(isinstance(tree.body, ast.Call))
        args = tree.body.args
        names = [astunparse.unparse(arg).strip() for arg in args]
        return names
    except Exception as ex:
        raise Exception('Cannot determine arg names') from None


def id_to_str(id_):
    """Return id as fixed-length hex."""
    if id_ < 0:
        id_ += 2 ** OS_BITS
    return f'0x{id_:0{OS_BITS//4}x}'

def hash_to_str(hash_):
    """Return hash as fixed-length hex."""
    return id_to_str(hash_)


class InvocationError(RuntimeError):
    pass

class CheckInvocation:
    """Check if exception comes from the function body or maybe from the fact
    that it is invoked incorrectly.
    """

    def __init__(self, caller_stack_depth=1):
        self.caller_stack_depth = caller_stack_depth

    def __enter__(self):
        pass

    def __exit__(self, ex_type, ex_value, tb):

        def get_stack_depth(tb=None):
            depth = 0
            while True:
                try:
                    tb = tb.tb_next
                except AttributeError:
                    break
                depth += 1
            return depth

        if ex_value:
            exc_stack_depth = get_stack_depth(tb)
            if exc_stack_depth == self.caller_stack_depth:
                raise InvocationError(ex_value) from None

class NoException(RuntimeError):
    def __init__(self, return_value):
        super().__init__("no exception raised")
        self.return_value = return_value

def catch(func):
    """Return wrapper that executes target function and return exception raised
    by this target function. If no exception is raised by the target function,
    wrapper raises NoException."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return_value = func(*args, **kwargs)
        except Exception as ex:
            return ex
        else:
            raise NoException(return_value) from None
    return wrapper

def nth(iterable, index):
    """Get `index`-nth element from iterable."""
    return [*islice(iterable, index, index+1)][0]


def prettify_expr(expr):

    def pretty_string(s, *args, **kwargs):
        return repr(s)

    def pretty_source(source):
        return ''.join(source)

    tree = ast.parse(expr)
    pretty = astor.code_gen.to_source(tree, pretty_string=pretty_string, pretty_source=pretty_source).strip()

    # alternatively do:
    # pretty = black.format_str(expr, line_length=math.inf).strip()

    return pretty

def crayon_expr(expr):
    return highlight(expr, PythonLexer(), TerminalFormatter()).strip()

def exc_to_str(exc, show_type=False):

    def try1():
        return exc.msg

    def try2():
        return str(exc)

    tries = [try1, try2]

    ret = ""
    for t in tries:
        try:
            ret = t()
            if ret:
                break
        except Exception:
            pass

    type_name = type(exc).__name__

    if ret:
        if show_type:
            return f"{type_name}: {ret}"
        else:
            return ret
    else:
        return type_name

def pformat(expr):
    # alternatively: pprint.pformat
    return pprintpp.pformat(expr)
