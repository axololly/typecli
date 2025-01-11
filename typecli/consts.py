class consts:
    BUILD_AND_RUN: bool = True
    """
    A constant defining whether or not the code should build a CLI after code terminates.

    This functions like .NET's top-level statements where code is automatically translated
    into the default scheme before being run. In this case, a `CLI` is created and is run
    after the program terminates.

    If you want to build a `CLI` instance yourself, disable this feature.
    """