type RGB = tuple[int, int, int]
type ANSIColour = str

DEFAULT_END = '\u001b[37m' # White

def rgb(rgb: RGB, text: str, /) -> ANSIColour:
    return f"\u001b[38;2;{rgb[0]};{rgb[1]};{rgb[2]}m{text}{DEFAULT_END}"

def hex(val: int, text: str, /) -> ANSIColour:
    rgb_vals = (val >> 16 & 255, val >> 8 & 255, val & 255)

    return rgb(rgb_vals, text)

def error(message: str, /) -> None:
    "Prints a coloured error message to the screen."
    
    print(hex(0xde0202, message))

def warn(message: str, /) -> None:
    "Prints a coloured warning message to the screen."

    print(hex(0xcdd424, message))