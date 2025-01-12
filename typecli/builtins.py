from .colour import error, warn
from .commands import command, Command
from . import types
from .types import *

from inspect import cleandoc
from rich.console import Console
from rich.markdown import Markdown

@command()
def echo(text: Sentence, /) -> None:
    "Echoes back the text given to it."
    
    print(text)


@command()
def help(name: Word, /) -> None:
    "Lists the documentation of the given command or type."

    command = Command.instances.get(name)

    if command:
        if command.description == "No description provided.":
            warn(f"No description given for command '{name}'.")
            return

        doc = cleandoc(f"# Help on command '{command.name}':\n{command.description}")
        md = Markdown(doc)

        Console().print(md)
        print()

        return

    attrs = set(dir(types)) - set(dir(object))
    cli_types = [
        getattr(types, attr) for attr in attrs
        if attr[0].isupper()
        and not attr.startswith('__')
    ]

    type_lookup: dict[str, object] = {
        T.__name__: T
        for T in cli_types
    }

    cli_type = type_lookup.get(name)

    if cli_type:
        doc = cleandoc(f"# Help on type '{name}':\n{cli_type.__doc__}")
        md = Markdown(doc)

        Console().print(md)
        print()

        return
    
    error(f"Cannot find an object by the name '{name}'.")