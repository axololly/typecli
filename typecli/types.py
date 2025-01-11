class _BuiltinMeta(type):
    def __init__(cls, *_) -> None:
        if len(cls.__mro__) > 3:
            raise NotImplementedError("this type cannot be subclassed.")
    
    def __repr__(self) -> str:
        return f"<built-in argument type '{self.__name__}'>"

class _BuiltinType(metaclass = _BuiltinMeta):
    def __init__(self) -> None:
        raise NotImplementedError("this type cannot be instantiated.")

# ============================================================================== #

class Char(_BuiltinType):
    "Represents a single character."

class Word(_BuiltinType):
    """
    Represents a single "word".

    This is the default type for untyped arguments.
    """

    # TODO: turn something like 'Hello world' into
    # a `Word` instead of a `Sentence`

class Sentence(_BuiltinType):
    "Greedy type that takes all content up until a keyworded argument is shown."

# ============================================================================== #

type Positional[T] = T
type Keyworded[T] = T