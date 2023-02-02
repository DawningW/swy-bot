import sys
if sys.platform.startswith("win32") or sys.platform.startswith("cygwin"):
    from .windows import *
    from .console import *
else:
    try:
        from android.os import Build
    except ImportError:
        from .linux import *
        from .console import *
    else:
        from .android import *
