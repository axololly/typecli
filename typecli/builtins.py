from .commands import command
from .types import Positional, Sentence

@command()
def echo(text: Positional[Sentence]) -> None:
    print(text)