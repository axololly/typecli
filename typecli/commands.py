from .colour import warn
from inspect import cleandoc, Parameter, signature as sig
from functools import wraps
from types import GenericAlias
from .types import *
from typing import Any, Callable

type Func = Callable[..., Any]


class Callback:
    def __init__(self, func: Func) -> None:
        self._func = func
        self._parameters = clean_parameters(func)
    
    @property
    def parameters(self) -> list[Parameter]:
        return self._parameters
    
    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        return self._func(*args, **kwargs)


class CommandLookup:
    """
    A helper class that allows for searching commands by
    name and also by index.

    Allows for O(1) lookup time when searching for commands.
    """

    __slots__ = ('_name_to_index', '_stored_commands')

    def __init__(self) -> None:
        "Create an empty command lookup."

        self._name_to_index = {}
        self._stored_commands = []
    
    def __getitem__(self, index: int | str) -> 'Command':
        if isinstance(index, int):
            return self._stored_commands[index]
        elif isinstance(index, str):
            return self._stored_commands[
                self._name_to_index[index]
            ]
        else:
            raise TypeError(f"type '{type(index)}' is not a valid index type.")
    
    def append(self, command: 'Command', /) -> None:
        "Add a command to the list of commands."

        if command.name in self._name_to_index:
            raise ValueError(f"name '{command.name}' has already been taken by another command or alias. Choose a different name.")

        for alias in command.aliases:
            if alias in self._name_to_index:
                raise ValueError(f"alias '{alias}' has already been taken by another command. Choose a different alias.")
            
            self._name_to_index[alias] = len(self._stored_commands)

        self._name_to_index[command.name] = len(self._stored_commands)
        self._stored_commands.append(command)

    def get(self, name: str, /) -> 'Command | None':
        """
        Gets a command from the internal lookup table, returning
        `None` if it wasn't found.
        """
        
        if name not in self._name_to_index:
            return None
        
        return self[name]


class Command:
    instances: CommandLookup = CommandLookup()
    
    def __init__(
        self,
        *,
        name: str | None = None,
        description: str,
        aliases: list[str] = [],
        callback: Func
    ) -> None:
        self.name = name
        self.description = description
        self.aliases = aliases
        self.callback = Callback(callback)

        self.instances.append(self)
    
    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        self.callback(*args, **kwargs)
    
    def __repr__(self) -> str:
        return f"<Command name='{self.name}' callback=...>"


def command(*, name: str | None = None, aliases: list[str] = []) -> Callable[..., Command]:
    @wraps(command)
    def wrapper(func: Func) -> Command:
        return Command(
            name = name or func.__name__,
            description = cleandoc(func.__doc__ or "No description provided."),
            aliases = aliases,
            callback = func
        )

    return wrapper


def alias(**aliases: str) -> Callable[[Command], Command]:
    def wrapper(command: Command) -> Command:
        lookup = {
            param.name: (param, pos)
            for pos, param in enumerate(command.callback.parameters)
        }
        
        for old_name, new_name in aliases.items():
            if old_name not in lookup:
                raise LookupError(f"cannot find parameter by the name '{old_name}' in the function '{command.callback._func.__name__}'.")
        
            parameter, position = lookup[old_name]

            command.callback._parameters[position] = parameter.replace(name = new_name)

        return command
    
    return wrapper


def clean_parameters(func: Func) -> list[Parameter]:
    params = list(sig(func).parameters.values())

    encountered_sentence = False
    encountered_flags = False

    for i, param in enumerate(params):
        if param.annotation is Flag:
            if not encountered_flags:
                encountered_flags = True
            
            if param.kind is not param.KEYWORD_ONLY:
                raise TypeError("Flag types must be attached to a keyworded argument.")
            continue
        else:
            if encountered_flags:
                raise TypeError(f"parameter '{param.name}' cannot come after a flag type. Flags must be after all arguments.")
        
        if param.kind == param.empty:
            warn(f"parameter '{param.name}' is missing a typehint.")
        
        if isinstance(param.annotation, GenericAlias):
            annot = param.annotation

            if annot.__origin__ is Positional:
                if param.kind == param.KEYWORD_ONLY:
                    raise TypeError(f"parameter '{param.name}' is aliased as positional but programmed as keyworded.")

                if param.kind == param.POSITIONAL_ONLY:
                    warn(f"parmeter '{param.name}' is already a positional argument - type annotation is redundant.")

                params[i] = param.replace(
                    kind = param.POSITIONAL_ONLY,
                    annotation = annot.__args__[0]
                )
            
            elif annot.__origin__ is Keyworded:
                if param.kind == param.POSITIONAL_ONLY:
                    raise TypeError(f"parameter '{param.name}' is aliased as keyworded but programmed as postional.")
                
                if param.kind == param.KEYWORD_ONLY:
                    warn(f"parmeter '{param.name}' is already a positional argument - type annotation is redundant.")
                
                params[i] = param.replace(
                    kind = param.KEYWORD_ONLY,
                    annotation = annot.__args__[0]
                )
            
            else:
                raise TypeError(f"unsupported generic alias typehint: '{param.annotation}'.")
            
            continue
        
        if param.kind == param.POSITIONAL_OR_KEYWORD:
            raise TypeError(f"ambiguously positioned parameters like parameter '{param.name}' are currently not supported.")
        
        if param.annotation not in (Char, Word, Sentence, int, float):
            raise TypeError(f"parameter '{param.name}' has an illegal annotation: '{param.annotation}'.")

        if param.annotation == Sentence:
            if encountered_sentence and param.kind == param.POSITIONAL_ONLY:
                raise TypeError(f"positional parameter '{param.kind}' cannot come after Sentence type.")

            encountered_sentence = True
    
    return params