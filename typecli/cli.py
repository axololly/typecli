from .commands import Command, CommandLookup
from .parser import Parser

class CLI:
    def __init__(self) -> None:
        self._commands: CommandLookup = Command.instances
    
    def run(self) -> None:
        Parser(self._commands).run()