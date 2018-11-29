import sys
import os
from math import ceil, log2

OS_IS_WINDOWS = os.name == 'nt'

# https://docs.python.org/3/library/platform.html#cross-platform
# read paragraph on platform.architecture()
OS_BITS = 2**ceil(log2(log2(sys.maxsize)))

dev_mode_enabled = bool(int(os.getenv('PEEPSHOW_DEV_MODE', 0)))
