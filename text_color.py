class TextStyle:
    RESET = "\033[0m"

class TextColor:
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    RED = "\033[31m"
    MAGENTA  = "\033[35m"
    CYAN  = "\033[36m"
    GREY = "\033[37m"
    WHITE = "\033[37m"

class TextBackground:
    GREEN = "\033[42m"   # fondo verde: representa la parte "completada"
    GREY  = "\033[100m"   # fondo gris oscuro brillante: representa la parte "vacía"
    RESET = "\033[10m"

COLORS = {
    "GREEN": TextColor.GREEN,
    "YELLOW": TextColor.YELLOW,
    "RED": TextColor.RED,
    "MAGENTA": TextColor.MAGENTA,
    "CYAN": TextColor.CYAN,
    "GREY": TextColor.GREY,
}

def color_message(msg, text_color, backg=TextBackground.RESET):
    color = COLORS.get(text_color, TextStyle.RESET)
    return f'{backg}{color}{msg}{TextStyle.RESET}'

# for msg, color in [("+K+", "RED"), ("<*>", "CYAN"), (" * ", "YELLOW"), (">!<", "MAGENTA"), ("   ", "GREY")]:
    # print(f'{color_message(msg, color)}')

