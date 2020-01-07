import sys

supported_versions = ('3.6', '3.7', '3.8')
python_version = '.'.join(map(str, sys.version_info[:2]))
if python_version not in supported_versions:
    raise RuntimeError('python version ' + python_version + ' is not supported')

from peepshow.peep import peep, peep_
from peepshow.show import show, show_
from peepshow.utils.python import catch
from peepshow.utils.python import nth
from peepshow.utils.traceback import enable_except_hook
