import re
import os
import shutil
import inspect
import subprocess
from pathlib import Path
from miscutils.insp import isaccess
import peepshow
import peepshow.core.dialect as dialect
import peepshow.core.trans as trans
from peepshow.cmds.base import CommandsBase, command
from peepshow.core import goto, probes
from peepshow.core.probes import read_features, MAJOR_FEATURES, MINOR_FEATURES
from peepshow.core.probes import is_subscribable
from peepshow.core.probes import Text, is_of_builtin_type
from peepshow.utils.terminal import print_help, print_error
from peepshow.utils.terminal import style, Style, Fore, Back
from peepshow.utils import terminal
from peepshow.pager import pager
from peepshow.core.exceptions import CommandError
from peepshow.utils.python import exc_to_str, crayon_expr, pformat
from peepshow.utils.traceback import FrameSummary

def table_width(table):
    return max(map(len, table)) + 1

def print_target_features(obj, features, *, hlight=False, header=None):
    table = read_features(obj, features)
    width = table_width(table)
    def get_lines():
        if header is not None:
            yield header
        for name, feat in table.items():
            line = f'{name:<{width}}: {feat}'
            if hlight and feat.value:
                line = style(Style.BRIGHT, line)
            yield line
    pager.page(get_lines())

class Commands(CommandsBase):

    def __init__(self, context):
        self.ctx = context

    def qualifier_cmd_eval(alias):
        regexp = re.compile('!(.*)$')
        m = regexp.match(alias)
        return m.groups()[0]

    @command('!<EXPR>', qualifier_cmd_eval)
    def cmd_eval(self, expr):
        """Evaluate <EXPR> and print the result.
        Empty <EXPR> will paste expression of current target and let you edit it.
        See also '$<EXPR>' command.
        """

        expr = expr.strip()
        if expr:
            try:
                try:
                    result = self.ctx.eval_(expr)
                    print(repr(result))
                except SyntaxError:
                    self.ctx.exec_(expr)
            except Exception as ex:
                raise CommandError(exc_to_str(ex, show_type=True)) from ex
            terminal.update_suggestions(self.ctx.env.current)
        else:
            expr = dialect.Evaluable().stringify(self.ctx.mgr.selected)
            terminal.prefill_input('!' + expr)

    def qualifier_cmd_eval_get(alias):
        regexp = re.compile(r'\$(.*)$')
        m = regexp.match(alias)
        return m.groups()[0]

    @command('$<EXPR>', qualifier_cmd_eval_get)
    def cmd_eval_get(self, expr):
        """Evaluate <EXPR> and consider result as a new target.
        Empty <EXPR> will paste expression of current target and let you edit it.
        See also '!<EXPR>' command.
        """

        expr = expr.strip()

        if expr:
            self.ctx.mgr.transform(trans.Eval(expr))
            return Commands.cmd_info, (self,)
        else:
            expr = dialect.Evaluable().stringify(self.ctx.mgr.selected)
            terminal.prefill_input('$' + expr)

    def qualifier_cmd_index(alias):
        regexp = re.compile('\[(.+)\]$')
        m = regexp.match(alias)
        return m.groups()[0]

    @command('[<EXPR>]', qualifier_cmd_index)
    def cmd_index(self, expr):
        """Subscribe target with <EXPR>."""

        if not probes.is_subscribable(self.ctx.target):
            raise CommandError("Item not subscribable.")

        self.ctx.mgr.transform(trans.SubscrExpr(expr))
        return Commands.cmd_info, (self,)

    def qualifier_cmd_call(alias):
        regexp = re.compile('\((.*)\)$')
        m = regexp.match(alias)
        return m.groups()[0]

    @command('(<ARGS>)', qualifier_cmd_call)
    def cmd_call(self, args_kwargs_str):
        """Call target with <ARGS>."""

        if not probes.is_callable(self.ctx.target):
            raise CommandError("Item not callable.")

        try:
            self.ctx.mgr.transform(trans.Call(args_kwargs_str))
        except Exception as ex:
            raise CommandError(f'Invalid invocation: {exc_to_str(ex)}') from ex

        return Commands.cmd_info, (self,)

    @command('ShowCache')
    def cmd_buffer(self):
        """Show content of cache which can be accessed by <INT> command.
        See also '<INT>' command.
        """
        self.ctx.explorer.recall()

    @command('DirAll')
    def cmd_dir_all(self):
        """Call dir(<TARGET>) and show all the results.
        See also 'Dir' and 'DirPublic' commands.
        """
        target = self.ctx.target
        content = self.ctx.mgr.propose_attr(dir(target))
        self.ctx.explorer.fill(content, 'attr')

    @command('Dir')
    def cmd_dir(self):
        """Call dir(<TARGET>) and show results other than of __XYZ__ format.
        See also 'DirAll' and 'DirPublic' commands.
        """
        target = self.ctx.target
        cond = lambda k: not isaccess(k).special
        attr_names = filter(cond, dir(target))
        content = self.ctx.mgr.propose_attr(attr_names)
        self.ctx.explorer.fill(content, 'attr')

    @command('DirPublic')
    def cmd_dir_public(self):
        """Call dir(<TARGET>) and show results other than starting with '_'.
        See also 'Dir' and 'DirAll' commands.
        """
        target = self.ctx.target
        cond = lambda k: isaccess(k).public
        attr_names = filter(cond, dir(target))
        content = self.ctx.mgr.propose_attr(attr_names)
        self.ctx.explorer.fill(content, 'attr')

    @command('Vars')
    def cmd_vars(self):
        """Call vars(<TARGET>) and show all the results.
        See also 'VarsPublic' command.
        """
        target = self.ctx.target
        try:
            v = vars(target)
        except Exception as ex:
            raise CommandError(exc_to_str(ex))

        content = self.ctx.mgr.propose_attr(v.keys(), v.values())
        self.ctx.explorer.fill(content, 'attr')

    @command('VarsPublic')
    def cmd_vars_public(self):
        """Call vars(<TARGET>) and show results other than starting with '_'.
        See also 'Vars' command.
        """
        target = self.ctx.target
        try:
            v = vars(target)
        except Exception as ex:
            raise CommandError(exc_to_str(ex))

        items = ((k, v) for k,v in vars(target).items() if isaccess(k).public)
        try:
            keys, values = zip(*items)
        except ValueError:
            keys, values = (), ()
        content = self.ctx.mgr.propose_attr(keys, values)
        self.ctx.explorer.fill(content, 'attr')

    @command('<INT>', int)
    def cmd_int(self, x):
        """Select <INT>-th item from cache.
        See also 'ShowCache' command.
        """

        transformation = self.ctx.explorer.get_transformation(x)
        self.ctx.mgr.accept(transformation)
        return Commands.cmd_info, (self,)

    @command('..')
    def cmd_back(self):
        """Make one step backward in history.
        See also '-', '/', '.' commands.
        """
        try:
            self.ctx.mgr.select_prev()
            return Commands.cmd_info, (self,)
        except IndexError:
            raise CommandError(f"This is the first item in history. Cannot go back any more.")

    @command('-')
    def cmd_forward(self):
        """Make one step forward in history.
        See also '..', '/', '.' commands.
        """
        try:
            self.ctx.mgr.select_next()
            return Commands.cmd_info, (self,)
        except IndexError:
            raise CommandError("This is the last item in history. Cannot go forward any more.")

    @command('/')
    def cmd_root(self):
        """Go to the begining in history.
        See also '..', '-', '.' commands.
        """
        self.ctx.mgr.select_first()
        return Commands.cmd_info, (self,)

    @command('.')
    def cmd_history(self):
        """Display history.
        See also '..', '-', '/' commands.
        """
        for entry, current in self.ctx.mgr.get_history(dialect.Readable()):
            if current:
                print(style(Style.BRIGHT, entry))
            else:
                print(entry)

    def qualifier_cmd_iterate(alias):
        regexp = re.compile('\*(\d*)$')
        m = regexp.match(alias)
        return int('0' + m.groups()[0])

    @command('*<OFFSET>', qualifier_cmd_iterate)
    def cmd_iterate(self, offset):
        """Iterate target.
        This can be used for listing values of iterable.
        Optional <OFFSET> can be used for skipping certain number of entires.
        """
        target = self.ctx.target
        try:
            content = self.ctx.mgr.propose_iter(offset) # TODO offset
        except TypeError:
            raise CommandError("Item is not iterable.")
        self.ctx.explorer.fill(content, 'list', offset)

    def qualifier_cmd_items(alias):
        regexp = re.compile('\*\*(\d*)$')
        m = regexp.match(alias)
        return int('0' + m.groups()[0])

    @command('**<OFFSET>', qualifier_cmd_items)
    def cmd_items(self, offset):
        """Call <TARGET>.items() and iterate through results.
        This can be used for listing keys and values of the dictionary.
        Optional <OFFSET> can be used for skipping certain number of entires.
        """
        target = self.ctx.target
        try:
            keys = target.keys()
        except Exception as ex:
            raise CommandError(exc_to_str(ex))

        try:
            content = self.ctx.mgr.propose_subscr(keys)
        except:
            raise CommandError("Error while obtaining items to iterate.")
        self.ctx.explorer.fill(content, 'dict', offset)

    def qualifier_cmd_attrib(alias):
        regexp = re.compile('\.([A-Za-z_][A-Za-z0-9_]*)$')
        m = regexp.match(alias)
        return m.groups()[0]

    @command('.<ATTRIB>', qualifier_cmd_attrib)
    def cmd_attrib(self, attr_name):
        """Return attribute <ATTRIB> of the target.
        """
        try:
            self.ctx.mgr.transform(trans.Attrib(attr_name))
        except:
            raise CommandError(f"Attribute cannot be obtained.")
        return Commands.cmd_info, (self,)

    @command('Continue')
    def cmd_continue(self):
        """Exit peepshow and continue execution of underlying application.
        Alternatively enter EOF (under Linux press: CTRL+D)
        See also 'Quit' and 'Export' commands.
        """
        raise goto.Stop(exit=False)

    @command('Quit')
    def cmd_quit(self):
        """Exit peepshow and terminate underlying Python interpreter.
        Alternatively send SIGINT (under Linux press: CTRL+C)
        See also 'Continue' and 'Export' commands.
        """
        raise goto.Stop(exit=True)

    @command('Export')
    def cmd_export(self):
        """Export target expression to IPython.
        This terminates peepshow and initiates next command in underlying IPython
        with the expression describing current target.
        See also 'Continue' and 'Quit' commands.
        """
        try:
            import IPython
            ip = IPython.get_ipython()
            expr = dialect.Evaluable().stringify(self.ctx.mgr.selected)
            ip.set_next_input(expr)
        except:
            raise CommandError("IPython is not available.")
        raise goto.Stop(exit=False)

    @command('?')
    def cmd_docstring(self):
        """Show docstring of the target."""
        try:
            print(inspect.cleandoc(self.ctx.target.__doc__))
        except Exception as ex:
            raise CommandError('Cannot read docstring.')

    @command('??')
    def cmd_source(self):
        """Show source code of the target."""
        try:
            target = self.ctx.target
            if isinstance(target, FrameSummary):
                file_name = target.file_name
                first_line_no = target.line_no
                first_line_no = max(first_line_no, 1)
                variable_list = '\n'.join(f'{name}={value}' for name, value in target.gloloc.items())
                cmd = ('vim', '-', '--not-a-term', '-c', ':set syntax=config', '-c', f'vsplit {file_name}', '-c', 'map q :qa<CR>', '-c', 'map <CR> :qa<CR>', '-c', ':set number', '-RM', f'+{first_line_no}', '-c', 'normal zt')
                p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
                p.stdin.write(variable_list.encode())
                p.communicate()
            else:
                file_name = inspect.getsourcefile(target)
                _, first_line_no = inspect.getsourcelines(target)
                first_line_no = max(first_line_no, 1)
                shell_cmd = f'vim --not-a-term -c "map q :qa<CR>" -c "map <CR> :qa<CR>" -c ":set number" -RM +{first_line_no} -c "normal zt" {file_name}'
                os.system(shell_cmd)
        except Exception as ex:
            raise CommandError('Cannot find source code.')

    @command('Help', syntax='<CMD>')
    def cmd_help(self, alias=None):
        """Show list of available commands or context help on given command.
        <CMD> is optional and can be either full command name or just a nick
        (capital leters from the name).
        See also 'MANual' command.
        """
        if alias is None:
            print_help('Available commands:')
            print_help()

            def get_summary(cmd):
                try:
                    docstr = inspect.cleandoc(cmd.__doc__)
                except:
                    return ''
                return (docstr + '\n').splitlines()[0]


            def get_header(cmd):
                return ' '.join( (p for p in (cmd.cmd_descr.name, cmd.cmd_descr.syntax) if p))

            entires = [(get_header(cmd), get_summary(cmd)) for cmd in self]
            headers, summaries = zip(*entires)
            left_margin = '  '
            col_sep = '    '
            left_col_width = max(map(len, headers))
            lines = (f"{left_margin}{header:<{left_col_width}}{col_sep}{summary}" for header, summary in entires)
            print_help('\n'.join(sorted(lines, key=lambda x: x.lower())))
            print_help()
            print_help('Use either full command name or just capital leters from it (nick).')
            print_help('Whatever you type, it is case-insensitive.')
            print_help('E.g. you can invoke help by typing: h, H, help, Help, HeLp')
            print_help()
            print_help('Some of the commands have also keyboard bindings assigned.')
            print_help('Invoke "help CMD" for more help on specific command.')
        else:
            try:
                cmd_hdlr, _ = self[alias]
            except KeyError:
                cmds_custom = {cmd.cmd_descr.name.lower(): cmd for cmd in self if callable(cmd.cmd_descr.qualifier)}
                try:
                    cmd_hdlr = cmds_custom[alias.lower()]
                except KeyError:
                    raise CommandError(f'No such command: {alias}.')

            if cmd_hdlr.__doc__:
                parts = ('Syntax:', cmd_hdlr.cmd_descr.name, cmd_hdlr.cmd_descr.syntax)
                print_help(' '.join( (p for p in parts if p) ))
                print_help(inspect.cleandoc(cmd_hdlr.__doc__))
            else:
                raise CommandError(f"No help on '{cmd_hdlr.cmd_descr.name}'.")

    @command('MANual')
    def cmd_man(self):
        """Show manual of peepshow.
        See also 'Help' command.
        """
        man_path = Path(peepshow.__path__[0]) / 'peepshow.1'
        os.system(f'man -l {man_path}')

    @command('Info')
    def cmd_info(self):
        """Show basic information about the target object.
        See also 'Features' command.
        """
        expr = f'{self.ctx.readable:^{shutil.get_terminal_size().columns}}'
        header = style(Back.LIGHTBLUE_EX + Fore.WHITE + Style.BRIGHT, expr)
        terminal.clear()
        print_target_features(self.ctx.target, MAJOR_FEATURES, hlight=True, header=header)
        self.ctx.only_info_visible = True

    @command('Features')
    def cmd_features(self):
        """Show detailed features of the target.
        Results are obtained by 'inspect' module.
        See also 'Info' command.
        """
        print_target_features(self.ctx.target, MINOR_FEATURES, hlight=True)

    @command('CLear')
    def cmd_clear(self):
        """Clear the terminal.
        Alternatively (under Linux) press: CTRL+L
        """
        terminal.clear()

    @command('Type')
    def cmd_type(self):
        """Type of the target becomes a new target."""
        self.ctx.mgr.transform(trans.Pass(type))
        return Commands.cmd_info, (self,)

    @command('Pass', syntax='<FUNC>')
    def cmd_pass(self, func_name):
        """Pass target as an argument to a function."""
        self.ctx.mgr.transform(trans.PassExpr(func_name))
        return Commands.cmd_info, (self,)

    @command('Self')
    def cmd_self(self):
        """Bound object becomes a new target."""
        try:
            self.ctx.mgr.transform(trans.Attrib('__self__'))
        except:
            raise CommandError(f"This target doesn't have bound object.")
        return Commands.cmd_info, (self,)

    @command('Bases')
    def cmd_bases(self):
        """Tuple of base classes of the target becomes a new target.
        See also 'Mro' command.
        """
        try:
            self.ctx.mgr.transform(trans.Attrib('__bases__'))
        except:
            raise CommandError(f"This target doesn't have bases.")
        return Commands.cmd_info, (self,)

    @command('Mro')
    def cmd_mro(self):
        """MRO list of the target becomes a new target.
        See also 'Bases' command.
        """
        try:
            self.ctx.mgr.transform(trans.Attrib('__mro__'))
        except:
            raise CommandError(f'There is no MRO list corresponding to this target.')
        return Commands.cmd_info, (self,)

    @command('eXpression')
    def cmd_expression(self):
        """Print expression that evaluates to examined target.
        See also 'PrettyPrint' command.
        """
        expr = dialect.Evaluable().stringify(self.ctx.mgr.selected)
        print(crayon_expr(expr))

    @command('PrettyPrint')
    def cmd_pretty_print(self):
        """Print target recursively.
        See also 'eXpression' command.
        """
        print(pformat(self.ctx.target))
