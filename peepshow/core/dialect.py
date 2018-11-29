import ast
import peepshow.core.trans as trans
from peepshow.utils.python import prettify_expr

def _find_var_offsets(obj, var_name):
    ret = ()
    if isinstance(obj, ast.Name):
        if obj.id == var_name:
            ret = ((obj.col_offset,),)
    elif isinstance(obj, ast.AST):
        ret = tuple(_find_var_offsets(getattr(obj, field), var_name) for field in obj._fields)
    elif isinstance(obj, list):
        ret = tuple(_find_var_offsets(item, var_name) for item in obj)
    return sum(ret, ())


def replace_var_name(expr, var_name, replacement):
    tree = ast.parse(expr)
    offsets = _find_var_offsets(tree.body[0], var_name)

    bias = 0
    for start in offsets:
        start_biased = start + bias
        stop_biased = start_biased + len(var_name)
        expr = expr[:start_biased] + replacement + expr[stop_biased:]
        bias += len(replacement) - len(var_name)

    return expr

def is_dependent_expr(expr):
    return replace_var_name(expr, '_', '_') != replace_var_name(expr, '_', '')

def expr_low_prio(expr):
    try:
        kind = ast.parse(expr).body[0].value
    except:
        return True

    high_prio_objects = (
        ast.Num,
        ast.Str,
        ast.Name,
        ast.Dict,
        ast.Set,
        ast.Tuple,
        ast.List,
        ast.Call,
        ast.Subscript,
        ast.Attribute)

    # if anything unexpected comes, priority is assumed low
    return not isinstance(kind, high_prio_objects)

def expr_num_literal(expr):
    try:
        kind = ast.parse(expr).body[0].value
    except:
        return False

    return isinstance(kind, ast.Num)

def add_panth(expr):
    return f"({expr})"

class Dialect:

    def stringify(self, obj):
        return obj.stringify(self)

    def is_prev_low_prio(self, transformation):
        raise NotImplementedError

    def is_prev_num_literal(self, transformation):
        prev_trans = transformation.get_prev()
        if isinstance(prev_trans, (trans.Given, trans.Eval)):
            return expr_num_literal(prev_trans.expr)
        return False

    def apply(self, transformation, prev_str=None):
        cls = type(transformation)
        hndl_name = 'fmt_' + cls.__name__.lower()
        hndl = getattr(self, hndl_name)
        return hndl(x=prev_str, t=transformation)

# Depreciated
class EvaluableCustom(Dialect):

    def is_prev_low_prio(self, transformation):
        prev_trans = transformation.get_prev()
        if prev_trans is None:
            return False
        elif isinstance(prev_trans, (trans.GloLoc,
                                     trans.Iter,
                                     trans.Attrib,
                                     trans.Pass,
                                     trans.PassExpr,
                                     trans.Call,
                                     trans.Subscr,
                                     trans.SubscrExpr,
                                     trans.Iter)):
            return False
        elif isinstance(prev_trans, (trans.Given, trans.Eval)):
            return expr_low_prio(prev_trans.expr)
        else:
            return True

    def add_panth(self, x, t):
        if self.is_prev_low_prio(t) or self.is_prev_num_literal(t):
            return add_panth(x)
        else:
            return x

    def fmt_gloloc(self, x, t):
        return '{**globals(), **locals()}'

    def fmt_given(self, x, t):
        return t.expr

    def fmt_attrib(self, x, t):
        x = self.add_panth(x, t)
        return f'{x}.{t.attr_name}'

    def fmt_pass(self, x, t):
        return f'{t.func_name}({x})'

    def fmt_passexpr(self, x, t):
        return f'{t.func_name}({x})'

    def fmt_call(self, x, t):
        if t.catched:
            return f'catch({x})({t.args_kwargs})'
        else:
            x = self.add_panth(x, t)
            return f'{x}({t.args_kwargs})'

    def fmt_subscr(self, x, t):
        if isinstance(t.get_prev(), trans.GloLoc):
            return f'{t.index}'
        else:
            x = self.add_panth(x, t)
            return f'{x}[{t.index!r}]'

    def fmt_subscrexpr(self, x, t):
        x = self.add_panth(x, t)
        return f'{x}[{t.expr}]'

    def fmt_iter(self, x, t):
        return f'nth({x}, {t.index!r})'

    def fmt_eval(self, x, t):
        if is_dependent_expr(t.expr):
            x = self.add_panth(x, t)
            return replace_var_name(t.expr, '_', x)
        else:
            return t.expr


class EvaluableAuto(Dialect):

    def stringify(self, obj):
        return prettify_expr(obj.stringify(self))

    def fmt_gloloc(self, x, t):
        return '{**globals(), **locals()}'

    def fmt_given(self, x, t):
        return t.expr

    def fmt_attrib(self, x, t):
        x = add_panth(x)
        return f'{x}.{t.attr_name}'

    def fmt_pass(self, x, t):
        return f'{t.func_name}({x})'

    def fmt_passexpr(self, x, t):
        return f'{t.func_name}({x})'

    def fmt_call(self, x, t):
        if t.catched:
            return f'catch({x})({t.args_kwargs})'
        else:
            x = add_panth(x)
            return f'{x}({t.args_kwargs})'

    def fmt_subscr(self, x, t):
        if isinstance(t.get_prev(), trans.GloLoc):
            return f'{t.index}'
        else:
            x = add_panth(x)
            return f'{x}[{t.index!r}]'

    def fmt_subscrexpr(self, x, t):
        x = add_panth(x)
        return f'{x}[{t.expr}]'

    def fmt_iter(self, x, t):
        return f'nth({x}, {t.index!r})'

    def fmt_eval(self, x, t):
        if is_dependent_expr(t.expr):
            x = add_panth(x)
            return replace_var_name(t.expr, '_', x)
        else:
            return t.expr

Evaluable = EvaluableAuto

class Readable(Dialect):

    def is_prev_low_prio(self, transformation):
        prev_trans = transformation.get_prev()
        if prev_trans is None:
            return False
        elif isinstance(prev_trans, (trans.GloLoc,
                                     trans.Iter,
                                     trans.Attrib,
                                     trans.Call,
                                     trans.Subscr,
                                     trans.SubscrExpr)):
            return False
        elif isinstance(prev_trans, (trans.Given, trans.Eval)):
            return expr_low_prio(prev_trans.expr)
        else:
            return True

    def add_panth(self, x, t):
        if self.is_prev_low_prio(t) or self.is_prev_num_literal(t):
            return add_panth(x)
        else:
            return x

    def fmt_gloloc(self, x, t):
        return '<*>'

    def fmt_given(self, x, t):
        return t.expr

    def fmt_attrib(self, x, t):
        x = self.add_panth(x, t)
        return f'{x}.{t.attr_name}'

    def fmt_pass(self, x, t):
        return f'{x} -> {t.func_name}'

    def fmt_passexpr(self, x, t):
        return f'{x} -> {t.func_name}'

    def fmt_call(self, x, t):
        if t.catched:
            return f'catch({x})({t.args_kwargs})'
        else:
            x = self.add_panth(x, t)
            return f'{x}({t.args_kwargs})'

    def fmt_subscr(self, x, t):
        if isinstance(t.get_prev(), trans.GloLoc):
            return f'{t.index}'
        else:
            x = self.add_panth(x, t)
            return f'{x}[{t.index!r}]'

    def fmt_subscrexpr(self, x, t):
        x = self.add_panth(x, t)
        return f'{x}[{t.expr}]'

    def fmt_iter(self, x, t):
        x = self.add_panth(x, t)
        return f'{x}<{t.index}>'

    def fmt_eval(self, x, t):
        expr = prettify_expr(t.expr)
        if is_dependent_expr(t.expr):
            return f'{x} => {expr}'
        else:
            return expr
