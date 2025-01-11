from .commands import Command
from .parser import Parser

class CLI:
    def __init__(self) -> None:
        self._commands: list[Command] = Command.instances
    
    def run(self) -> None:
        Parser(self._commands).run()