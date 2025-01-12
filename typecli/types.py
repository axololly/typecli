type Class = type

def only_static(cls: Class) -> Class:
    def cannotBe(verb: str, /) -> ...:
        def f(*args, **kwargs) -> ...:
            raise TypeError(f"this type cannot be {verb}.")
        
        return f

    cls.__init__ = cannotBe("instantiated")
    cls.__init_subclass__ = cannotBe("subclassed")

    return cls

class BuiltinMeta(type):
    def __repr__(self) -> str:
        return f"<built-in argument type '{self.__name__}'>"

class BuiltinType(metaclass = BuiltinMeta): ...

# ============================================================================== #

@only_static
class Char(str, BuiltinType):
    """
    Represents a single character.

    Code:
    ```py
    @command()
    def is_upper(x: Char, /) -> None:
        print(x.isupper())
    ```

    Usage:
    ```yml
    >>> example A
    True
    ```
    """

@only_static
class Word(str, BuiltinType):
    """
    Represents a single "word".

    This is the default type for untyped arguments, unless changed by `consts.DEFAULT_TYPEHINT`.

    Code:
    ```py
    @command()
    def length(text: Word, /) -> None:
        print(len(text))
    ```

    Usage:
    ```yml
    >>> length sandwich
    8
    >>> length "ham sandwich"
    12
    ```
    """

@only_static
class Sentence(str, BuiltinType):
    """
    Greedy type that takes all content up until a keyworded argument is shown.

    This is the type used in the built-in `echo` command.

    Code:
    ```py
    @command()
    def echo(text: Sentence, /) -> None:
        print(text)
    ```

    Usage:
    ```yml
    >>> echo hello world
    hello world
    ```
    """

@only_static
class Flag(BuiltinType):
    """
    A type that becomes a boolean representing whether or not it was included in
    the command line arguments.

    These **must** be at the end of the function arguments and **must** be
    keyworded arguments.

    Code:
    ```py
    @command()
    def calc(*, n1: int)
    ```
    """

# ============================================================================== #

type Positional[T] = T
type Keyworded[T] = T