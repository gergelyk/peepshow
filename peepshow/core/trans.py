from peepshow.core.exceptions import CommandError
from peepshow.utils.python import CheckInvocation, InvocationError
from peepshow.utils.python import prettify_expr, exc_to_str

class Transformation:
    def __init__(self):
        self.result = None
        self._prev = None
        self._next = None
        self.available = False

    def link(self, prev, *, forward=True):
        self._prev = prev
        if forward:
            prev._next = self

    def evaluate(self, prev, ctx):
        raise NotImplementedError

    def assign(self, result):
        self.result = result
        self.available = True

    def execute(self, prev, ctx, *, safe=False):
        try:
            result = self.evaluate(prev, ctx)
        except:
            if not safe:
                raise
        else:
            self.assign(result)

    def get_prev(self):
        if self._prev:
            return self._prev
        else:
            raise IndexError

    def get_next(self):
        if self._next:
            return self._next
        else:
            raise IndexError

    def get_first(self):
        if self._prev:
            return self._prev.get_first()
        else:
            return self

    def stringify(self, style):
        prev_str = self._prev.stringify(style)
        curr_str = style.apply(self, prev_str)
        return curr_str

class Initial(Transformation):
    def __init__(self, target):
        super().__init__()
        self.result = target

class GloLoc(Initial):
    def stringify(self, style):
        return style.apply(self)

class Given(Initial):
    def __init__(self, target, expr):
        super().__init__(target)
        self.expr = prettify_expr(expr)

    def stringify(self, style):
        return style.apply(self, self.expr)

class Attrib(Transformation):
    def __init__(self, attr_name):
        super().__init__()
        self.attr_name = attr_name

    def evaluate(self, prev, env):
        return getattr(prev.result, self.attr_name)

class Pass(Transformation):
    def __init__(self, func):
        super().__init__()
        self.func = func
        self.func_name = func.__name__

    def evaluate(self, prev, ctx):
        return self.func(prev.result)

class PassExpr(Transformation):
    def __init__(self, func_name):
        super().__init__()
        self.func_name = func_name

    def evaluate(self, prev, ctx):
        try:
            value = ctx.eval_(f"{self.func_name}(_)")
        except Exception as ex:
            raise CommandError(f"Invalid invocation: {exc_to_str(ex)}") from ex
        return value

class Call(Transformation):
    def __init__(self, args_kwargs):
        super().__init__()
        self.args_kwargs = args_kwargs
        self.catched = False

    def evaluate(self, prev, ctx):
        call = f'_({self.args_kwargs})'
        try:
            with CheckInvocation(caller_stack_depth=3):
                return ctx.eval_(call)
        except InvocationError as ex:
            raise CommandError(ex) from ex
        except Exception as ex:
            self.catched = True
            return ex

class Subscr(Transformation):
    def __init__(self, index):
        super().__init__()
        self.index = index

    def evaluate(self, prev, ctx):
        return prev.result[self.index]

class SubscrExpr(Transformation):
    def __init__(self, expr):
        super().__init__()
        self.expr = expr

    def evaluate(self, prev, ctx):
        try:
            value = ctx.eval_(f"_[{self.expr}]")
        except Exception as ex:
            raise CommandError(exc_to_str(ex, show_type=True)) from ex
        return value

class Iter(Transformation):
    def __init__(self, index):
        super().__init__()
        self.index = index

    def evaluate(self, prev, ctx):
        return iget(prev.result, self.index)

class Eval(Transformation):
    def __init__(self, expr):
        super().__init__()
        self.expr = expr

    def evaluate(self, prev, ctx):
        try:
            value = ctx.eval_(self.expr)
        except SyntaxError as ex:
            raise CommandError(exc_to_str(ex, show_type=True)) from ex
        return value

class TransformationMgr:
    def __init__(self, target, ctx):
        self.selected = None
        self._ctx = ctx
        self.reset(target)

    def reset(self, transformation):
        self.selected = transformation

    def transform(self, transformation):
        transformation.execute(self.selected, self._ctx)
        self.accept(transformation)

    def accept(self, transformation):
        transformation.link(self.selected)
        self.selected = transformation

    def propose_iter(self, offset):
        for index, item in enumerate(self.selected.result):
            transformation = Iter(index)
            transformation.link(self.selected, forward=False)
            transformation.assign(item)
            yield None, transformation

    def propose_attr(self, attr_names, values=None):
        if values is None:
            for attr_name in attr_names:
                transformation = Attrib(attr_name)
                transformation.link(self.selected, forward=False)
                transformation.execute(self.selected, self._ctx, safe=True)
                yield attr_name, transformation
        else:
            for attr_name, value in zip(attr_names, values):
                transformation = Attrib(attr_name)
                transformation.link(self.selected, forward=False)
                transformation.assign(value)
                yield attr_name, transformation

    def propose_subscr(self, indices, values=None):
        if values is None:
            for index in indices:
                transformation = Subscr(index)
                transformation.link(self.selected, forward=False)
                transformation.execute(self.selected, self._ctx, safe=True)
                yield repr(index), transformation
        else:
            for index, value in zip(indices, values):
                transformation = Subscr(index)
                transformation.link(self.selected, forward=False)
                transformation.assign(value)
                yield repr(index), transformation

    def select_next(self):
        self.selected = self.selected.get_next()

    def select_prev(self):
        self.selected = self.selected.get_prev()

    def select_first(self):
        self.selected = self.selected.get_first()

    def get_history(self, style):
        for item in self:
            yield style.stringify(item), item is self.selected

    def __iter__(self):
        item = self.selected.get_first()
        while True:
            yield item
            try:
                item = item.get_next()
            except IndexError:
                break
