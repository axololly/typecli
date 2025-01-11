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

    from sys import exception

    # Check to see if there was an exception
    # raised while the project was building
    if exception():
        return

    # Get all `Command` instances from the running file
    file_commands = [
        obj for obj in running_file.__dict__.values()
        if isinstance(obj, Command)
    ]

    if not file_commands:
        return

    # Build the CLI
    cli = CLI()
    cli._commands = file_commands

    # Run the CLI
    cli.run()