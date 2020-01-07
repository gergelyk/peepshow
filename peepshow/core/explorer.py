import inspect
from functools import partial
from peepshow.pager import cache as paged_cache
from peepshow.pager.cache import PagedCache
from peepshow.core.probes import is_subscribable, is_iterable, is_callable
from peepshow.utils.terminal import style, Style, Fore, Back
from peepshow.core.probes import Text, is_of_builtin_type
from peepshow.core.exceptions import CommandError
from peepshow.utils.traceback import FrameSummary

def get_signature(obj):
    try:
        return str(inspect.signature(obj))
    except:
        return '(?)'

def str_func(mode, item):
    name, transformation = item
    attr = transformation.result
    available = transformation.available

    base = None
    if available:
        braces = ''
        if is_callable(attr):
            try:
                builtin_name = attr.__name__
            except AttributeError:
                pass
            else:
                if builtin_name != name:
                    braces += builtin_name

            braces += get_signature(attr)
        if is_subscribable(attr):
            braces += '[]'
        if is_iterable(attr):
            braces += '*'

        if name or braces:
            name_color = fr'{style(Style.BRIGHT, name)}' if name else ''
            sep = ':' if mode == 'dict' else ''
            braces_color = fr'{style(Fore.LIGHTGREEN_EX, braces)}' if braces else ''
            base = ' '.join(x for x in (name_color, sep, braces_color) if x)

        if attr is None:
            type_name = None
            value = repr(attr)
        elif is_callable(attr):
            if inspect.isclass(attr):
                try:
                    type_name = type(attr).__name__
                except:
                    type_name = '?'
                type_name = f'<{type_name}>'
                type_name = style(Fore.LIGHTRED_EX, type_name)
                value = repr(str(attr))
            else:
                type_name = None
                value = None
        elif is_of_builtin_type(attr)[0]:
            type_name = None
            value = repr(attr).splitlines()[0] # what if multiline
        elif isinstance(attr, FrameSummary):
            type_name = None
            location = style(Fore.LIGHTRED_EX, f'{attr.file_name}:{attr.line_no}')
            callable_name = style(Fore.LIGHTBLUE_EX, f'[{attr.callable_name}]')
            code_line = attr.line
            value = f"{location} {callable_name} {code_line}"
        else:
            try:
                type_name = type(attr).__name__
            except:
                type_name = '?'
            type_name = f'<{type_name}>'
            type_name = style(Fore.LIGHTRED_EX, type_name)
            value = repr(str(attr))

        if value is not None:
            value = style(Fore.LIGHTBLUE_EX, value)

        info = [base, type_name, value]
    else:
        if name:
            base = fr'{style(Style.BRIGHT, name)}'
        info = [base, 'N/A']

    return ' '.join( (x for x in info if x) )


class Explorer:
    def __init__(self, ctx):
        self.ctx = ctx
        self.cache = PagedCache([])
        self.cached_target = None

    def fill(self, content, style, offset=0):
        """style: 'attr', 'list', 'dict'
        """
        str_func_styled = partial(str_func, style)
        try:
            self.cache = paged_cache.page(content, str_func_styled, offset)
        except paged_cache.TooManyInitialIterations as ex:
            raise CommandError(ex) from ex
        self.cached_target = self.ctx.target

    def recall(self):
        if self.ctx.target is not self.cached_target:
            raise CommandError('No cache for this target')
        self.cache.recall_cache()

    def get_transformation(self, index):
        if self.ctx.target is not self.cached_target:
            raise CommandError('No cache for this target')

        try:
            key, transformation = self.cache[index]
        except Exception as ex:
            raise CommandError(ex) from ex

        if not transformation.available:
            raise CommandError('Item not available')

        return transformation
