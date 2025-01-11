from inspect import _empty as EMPTY_PARAMETER, Parameter, signature as sig
from functools import wraps
from types import GenericAlias
from .types import *
from typing import Any, Callable

type Func = Callable[..., Any]

class Command:
    instances: list['Command'] = []
    
    def __init__(
        self,
        *,
        name: str | None = None,
        aliases: list[str] = [],
        callback: Func,
        _params: list[Parameter]
    ) -> None:
        self.name = name
        self.aliases = aliases
        self.callback = callback
        self._callback_params = _params

        self.instances.append(self)
    
    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        self.callback(*args, **kwargs)
    
    def __repr__(self) -> str:
        return f"<Command name='{self.name}' callback=...>"


def command(*, name: str | None = None, aliases: list[str] = []) -> Callable[..., Command]:
    @wraps(command)
    def wrapper(func: Func) -> Command:
        params = extract_parameters(func)

        return Command(
            name = name or func.__name__,
            aliases = aliases,
            callback = func,
            _params = params
        )

    return wrapper


def extract_parameters(func: Func) -> list[Parameter]:
    params = list(sig(func).parameters.values())

    encountered_sentence = False

    for i, param in enumerate(params):
        if param.kind == EMPTY_PARAMETER:
            raise TypeError(f"parameter '{param.name}' is missing a typehint.")
        
        if isinstance(param.annotation, GenericAlias):
            annot = param.annotation

            if annot.__origin__ is Positional:
                if param.kind == param.KEYWORD_ONLY:
                    raise TypeError(f"parameter '{param.name}' is aliased as positional but programmed as keyworded.")

                params[i] = param.replace(
                    kind = param.POSITIONAL_ONLY,
                    annotation = annot.__args__[0]
                )
            
            elif annot.__origin__ is Keyworded:
                if param.kind == param.POSITIONAL_ONLY:
                    raise TypeError(f"parameter '{param.name}' is aliased as keyworded but programmed as postional.")
                
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