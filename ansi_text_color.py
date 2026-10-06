class AnsiColor:
    """Class to hold values of ANSI color graphic mode for text"""

    ESC = "\033"
    CSI = "["

    GRAPHIC_MODE = {
        "RESET": 0,
        "BOLD": 1,
        "DIM": 2,
        "ITALIC": 3,
        "UNDERLINE": 4,
        "BLINKING": 5,
        "REVERSE": 7,
        "INVISIBLE": 8,
        "STRIKETHROUGH": 9
    }

    FG_COLOR = {
        "BLACK": 30,
        "RED": 31,
        "GREEN": 32,
        "YELLOW": 33,
        "BLUE": 34,
        "MAGENTA": 35,
        "CYAN": 36,
        "WHITE": 37,
        "DEFAULT": 39
    }

    BG_COLOR = {
        "BLACK": 40,
        "RED": 41,
        "GREEN": 42,
        "YELLOW": 43,
        "BLUE": 44,
        "MAGENTA": 45,
        "CYAN": 46,
        "WHITE": 47,
        "DEFAULT": 49
    }

    SEP = ";"
    TEXT_FORMAT = "m"

def make_color_code(fg_color:str, bg_color:str="", modes:str=None)->str:
    """Return an ANSI SGR code for fg/bg/modes. Empty bg/modes are omitted.
    modes can be a space-separated list of modes
    Example: make_color_code("GREEN", modes="BLINKING underline Italic")"""

    parts = [str(AnsiColor.FG_COLOR.get(fg_color.upper(), AnsiColor.FG_COLOR["DEFAULT"]))]
    if bg_color:
        parts.append(str(AnsiColor.BG_COLOR.get(bg_color.upper(), AnsiColor.BG_COLOR["DEFAULT"])))

    if modes:
        if isinstance(modes, str):
            modes = modes.upper().split()

        for m in modes:
            parts.append(str(AnsiColor.GRAPHIC_MODE.get(m, AnsiColor.GRAPHIC_MODE["RESET"])))

    # if mode:
        # parts.append(str(AnsiColor.GRAPHIC_MODE.get(mode, AnsiColor.GRAPHIC_MODE["RESET"])))

    return f'{AnsiColor.ESC}{AnsiColor.CSI}{AnsiColor.SEP.join(parts)}{AnsiColor.TEXT_FORMAT}'


def reset_color_code()->str:
    """Return the ANSI reset color code, to be appended after each color 
    so latter text will not be affected."""
    return f'{AnsiColor.ESC}{AnsiColor.CSI}{AnsiColor.GRAPHIC_MODE.get("RESET", 0)}{AnsiColor.TEXT_FORMAT}'


def text_color(msg:str, fg_color:str, bg_color:str="", modes:str=None)->str:
    """Helper function to use make_color_code and reset_color_code to have the complete sequence.
    Returns the complete string to print or use in a f-string."""
    return make_color_code(fg_color=fg_color, bg_color=bg_color, modes=modes) + msg + reset_color_code()


# Examples:
# print(f'{make_color_code(fg_color="CYAN")}Hola Mundo{reset_color_code()}')
# print(f'{make_color_code(fg_color="YELLOW", bg_color="RED", mode="BLINKING")}Esto blinkea!!!{reset_color_code()}')
# 
# print(f'{text_color("Hola estrella", "GREEN", modes="BLINKING underline Italic")}')
# print(f'{text_color("Caracola", "GREEN", modes="Italic")}')