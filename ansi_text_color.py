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

def make_color_code(fg_color, bg_color="", mode=""):
    return f'{AnsiColor.ESC}{AnsiColor.CSI}{AnsiColor.FG_COLOR.get(fg_color, 39)}\
{"" if bg_color == "" else AnsiColor.SEP + str(AnsiColor.BG_COLOR.get(bg_color, 49))}\
{"" if mode == "" else AnsiColor.SEP + str(AnsiColor.GRAPHIC_MODE.get(mode, 1))}\
{AnsiColor.TEXT_FORMAT}'


def reset_color_code():
    return f'{AnsiColor.ESC}{AnsiColor.CSI}{AnsiColor.GRAPHIC_MODE.get("RESET", 0)}{AnsiColor.TEXT_FORMAT}'


def text_color(msg, fg_color, bg_color="", mode=""):
    return make_color_code(fg_color=fg_color, bg_color=bg_color, mode=mode) + msg + reset_color_code()


# Examples:
# print(f'{make_color_code(fg_color="CYAN")}Hola Mundo{reset_color_code()}')
# print(f'{make_color_code(fg_color="YELLOW", bg_color="RED", mode="BLINKING")}Esto blinkea!!!{reset_color_code()}')
# 
# print(f'{text_color("Hola estrella", "GREEN", mode="BLINKING")}')