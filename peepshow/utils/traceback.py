import os
import sys
import traceback
import warnings
import inspect
from peepshow.peep import peep


class ExceptionSummary:
    def __init__(self, exc_type, exc_value, tb):
        self.exc_type = exc_type
        self.exc_value = exc_value
        self.tb = tb
        frames = [t[0] for t in traceback.walk_tb(tb)]
        self.frames = list(map(FrameSummary, frames))
        
    def __str__(self):
        return str(self.exc_value)
    
    def __repr__(self):
        return f'<ExceptionSummary for {self.exc_type.__name__}>'

    def __iter__(self):
        yield from self.frames

class FrameSummary:
    def __init__(self, frame):
        self.frame = frame
        self.line_no = frame.f_lineno
        self.file_name = frame.f_code.co_filename
        self.callable_name = frame.f_code.co_name
        try:
            with open(self.file_name) as fh:
                lines = fh.readlines()
                self.line = lines[self.line_no - 1].strip()
        except Exception:
            self.line = "<N/A>"
            
        self.gloloc = {**self.frame.f_globals, **self.frame.f_locals}

    def __repr__(self):
        return f"{self.file_name}:{self.line_no} [{self.callable_name}] {self.line}"

    def __getitem__(self, name):
        return self.gloloc[name]
    
    def keys(self):
        return self.gloloc.keys()
    
    def values(self):
        return self.gloloc.values()


def peep_except_hook(exc_type, exc_value, traceback):

    exc_stack = []
    while True:
        exc_stack.append(ExceptionSummary(exc_type, exc_value, traceback))
        if exc_value.__context__ is not None:
            exc_value = exc_value.__context__
            exc_type = type(exc_value)
            traceback = exc_value.__traceback__
            continue
        break 
    
    if len(exc_stack) == 1:
        peep(exc_stack[0])
    else:    
        peep(exc_stack)

def enable_except_hook(consider_env=False):
    try:
        if consider_env:
            enable = bool(int(os.getenv('PYTHON_PEEP_EXCEPTIONS', 0)))
        else:
            enable = true
    except (ValueError, TypeError):
        warnings.warn("Invalid value of PYTHON_PEEP_EXCEPTIONS", RuntimeWarning)
    else:
        if enable:
            sys.excepthook = peep_except_hook



