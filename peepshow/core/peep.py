import shlex
import sys
from peepshow.cmds.cmds import Commands, CommandError
from peepshow.utils import terminal
from peepshow.utils.terminal import print_error, print_help, style, Fore
from peepshow.utils.python import CheckInvocation, InvocationError
from peepshow.utils.system import dev_mode_enabled
from peepshow.core import goto
from peepshow.core.context import Context
from peepshow.core.probes import get_default_action, is_of_builtin_type
from peepshow.utils.python import exc_to_str

def read_command(ctx):
    try:
        _, _, type_name = is_of_builtin_type(ctx.target)
        if ctx.only_info_visible:
            action = get_default_action(ctx.target)
        else:
            action = 'i'

        type_name_color = style(Fore.LIGHTRED_EX, type_name, for_readline=True)
        type_name_color += ' ' if type_name else ''
        action_color = style(Fore.CYAN, action, for_readline=True)
        action_color += ' ' if action else ''

        cmd_raw = input(type_name_color + action_color + '> ').strip()
        terminal.prefill_input()
        if not cmd_raw:
            # execute suggested action:
            cmd_raw = action
            # just do nothing and print next prompt:
            #raise goto.NextCommand
        try:
            user_inp = shlex.split(cmd_raw, posix=True)
        except Exception as ex:
            print_error(f"Invalid syntax. {exc_to_str(ex)}.")
            raise goto.NextCommand

    except EOFError: # CTRL+D
        raise goto.Stop(exit=False)
    except KeyboardInterrupt: # CTRL+C
        raise goto.Stop(exit=True)

    cmd_alias, *cmd_usr_args = user_inp
    return cmd_raw, cmd_alias, tuple(cmd_usr_args)


def prepare_command(cmds, cmd_raw, cmd_alias, cmd_usr_args):
    try:
        try:
            cmd_hdlr, qualification = cmds[cmd_raw]
            cmd_usr_args = ()
        except KeyError:
            cmd_hdlr, qualification = cmds[cmd_alias]

        if qualification is not None:
            cmd_usr_args = (qualification, *cmd_usr_args)
    except KeyError:
        print_error(f"Unknown command '{cmd_alias}'.")
        cmd_hdlr = Commands.cmd_help
        cmd_usr_args = ()

    cmd_args = (cmds, *cmd_usr_args)
    return cmd_hdlr, cmd_args


def execute_command(ctx, cmd_hdlr, cmd_args):
    while True:
        try:
            ctx.only_info_visible = False

            try:
                with CheckInvocation():
                    new_cmd = cmd_hdlr(*cmd_args)
            except goto.GoToLabel:
                raise
            except InvocationError as ex:
                raise CommandError('Wrong number of arguments.') from ex
            except Exception as ex:
                raise CommandError(ex) from ex

            if new_cmd:
                cmd_hdlr, cmd_args = new_cmd
            else:
                break
        except goto.Stop:
            raise
        except CommandError as ex:
            if dev_mode_enabled:
                raise
            print_error("Error while executing command '{}'.".format(cmd_hdlr.cmd_descr.name))
            print_error(str(ex))
            cmds = cmd_args[0]
            cmd_args = (cmds, cmd_hdlr.cmd_descr.name)
            cmd_hdlr = Commands.cmd_help


def clean_up():
    terminal.clear()


def stop(try_exit):
    def test_exit():
        try:
            exit_func = exit
            return True
        except NameError:
            # e.g. in ipython exit() is not available
            return False

    cancel_stop = False
    if try_exit:
        if sys.gettrace():
            print_error('Underlying debugger cannot be terminated.')
            # in fact it can be, but in case of pdb/ipdb it results in an ugly exception
            print_help("You can use 'Continue' command to close peepshow.")
            cancel_stop = True
        elif test_exit():
            clean_up()
            exit(0)
        else:
            print_error('Underlying Python interpreter cannot be terminated.')
            print_help("You can use 'Continue' command to close peepshow.")
            cancel_stop = True
    else:
        clean_up()

    return cancel_stop


def peep(target, env):
    ctx = Context(target, env)
    terminal.init(ctx.env.current)
    cmds = Commands(ctx)
    execute_command(ctx, Commands.cmd_info, (cmds,))
    while True:
        try:
            cmd_raw, cmd_alias, cmd_usr_args = read_command(ctx)
            cmd_hdlr, cmd_args = prepare_command(cmds, cmd_raw, cmd_alias, cmd_usr_args)
            execute_command(ctx, cmd_hdlr, cmd_args)
        except goto.NextCommand:
            continue
        except goto.Stop as ex:
            if not stop(ex.exit):
                break

    return ctx.target
