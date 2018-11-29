import os
from colorama import Fore, Back, Style
import colorama
import rlcompleter
import readline
from peepshow.utils.system import OS_IS_WINDOWS

_completer_suggestions = {}

class Completer(rlcompleter.Completer):
    def complete_ex(self, *args, **kwargs):
        buf = readline.get_line_buffer().strip()
        if buf and buf[0] in ['!', '$']:
            return self.complete(*args, **kwargs)

def update_suggestions(suggestions):
    _completer_suggestions.update(suggestions)

def init(suggestions):
    update_suggestions(suggestions)
    completer = Completer(_completer_suggestions)
    readline.set_completer(completer.complete_ex)
    readline.parse_and_bind("tab: complete")
    colorama.init()
    readline.set_history_length(1000)
    clear()

def clear():
    os.system('cls' if OS_IS_WINDOWS else 'clear')

def print_error(msg='', *args, **kwargs):
    print(style(Back.RED + Fore.WHITE, msg), *args, **kwargs)

def print_help(msg='', *args, **kwargs):
    print(style(Fore.LIGHTYELLOW_EX, msg), *args, **kwargs)

def prefill_input(text=None):
    if text:
        readline.set_startup_hook(lambda: readline.insert_text(text))
    else:
        readline.set_startup_hook()

def style(spec, text, for_readline=False):
    # Thanks to Samuele Santi fot the article:
    # 9https://wiki.hackzine.org/development/misc/readline-color-prompt.html

    RL_PROMPT_START_IGNORE  = '\001'
    RL_PROMPT_END_IGNORE    = '\002'
    term = Style.RESET_ALL

    def wrap(text):
        if for_readline:
            return RL_PROMPT_START_IGNORE + text + RL_PROMPT_END_IGNORE
        else:
            return text

    return wrap(spec) + text + wrap(term)
