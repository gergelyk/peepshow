
# command name: e.g. DoSomething
# command nick: e.g. ds
# command alias: e.g. dosomething, DOSOMETHING, ds, DS, ...

from types import SimpleNamespace

def get_nick(name):
    return ''.join(filter(lambda k: 'A' <= k <= 'Z', name)).lower()

def command(name, qualifier=None, syntax=None):
    cmd_descr = SimpleNamespace(**locals())
    cmd_descr.nick = get_nick(name)

    def decorator(func):
        func.cmd_descr = cmd_descr
        return func
    return decorator


class CommandsBase:

    def __iter__(self):
        attrs = vars(type(self)).values()
        attrs = filter(callable, attrs)
        attrs = filter(lambda attr: hasattr(attr, 'cmd_descr'), attrs)
        yield from attrs

    def __getitem__(self, alias):
        if not alias:
            raise KeyError

        cmds_simple = [cmd for cmd in self if cmd.cmd_descr.qualifier is None]
        qualification = None

        # try to find command by name
        cmds_simple_by_name = {cmd.cmd_descr.name.lower(): cmd for cmd in cmds_simple}
        try:
            return cmds_simple_by_name[alias.lower()], qualification
        except KeyError:
            pass

        # try to find command by alias
        cmds_simple_by_nick = {cmd.cmd_descr.nick: cmd for cmd in cmds_simple}
        try:
            return cmds_simple_by_nick[alias.lower()], qualification
        except KeyError:
            pass

        # try to find command by qualifier
        cmds_custom = (cmd for cmd in self if callable(cmd.cmd_descr.qualifier))
        for cmd in cmds_custom:
            try:
                qualification = cmd.cmd_descr.qualifier(alias)
                return cmd, qualification
            except:
                pass

        raise KeyError
