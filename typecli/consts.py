from .types import BuiltinType, Word

class consts(BuiltinType):
    "A helper class that defines configuration constants for various aspects of the code."
    
    BUILD_AND_RUN: bool = True
    """
    A constant defining whether or not the code should build a CLI after code terminates.

    This functions like .NET's top-level statements where code is automatically translated
    into the default scheme before being run. In this case, a `CLI` is created and is run
    after the program terminates.

    If you want to build a `CLI` instance yourself, disable this feature.
    """

    WARN_MISSING_TYPEHINT: bool = True
    """
    A constant defining whether or not to warn users before startup of missing typehints.

    By default, these variables are annotated to be `Word` types. To change this, edit the
    `DEFAULT_TYPEHINT` constant.

    To remove these warnings, change this constant to be `False`.
    """

    DEFAULT_TYPEHINT: type = Word
    """
    A constant defining the default type of untyped arguments.

    This is usually `Word`, unless edited.
    """