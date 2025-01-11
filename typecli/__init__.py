from .cli import *
from .commands import *
from .consts import *
from .types import *

# =================================================================== #

from atexit import register as after_end

@after_end
def _build_and_run():
    from importlib import import_module
    
    running_file = import_module('__main__')
    
    if not consts.BUILD_AND_RUN:
        return

    # Check to see if there was an exception
    # raised while the project was building
    try:
        from sys import last_exc
        return
    except ImportError:
        pass

    # Build the CLI
    cli = CLI()

    # Run the CLI
    cli.run()