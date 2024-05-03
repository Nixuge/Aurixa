# Note:
# This is VERY sketchy
# only advantage is that it looks nice.
# I'll replace it one day.

import logging
from datetime import datetime

def load_proper_logger(logger: logging.Logger, debugConsole: bool):
    logger.setLevel(logging.DEBUG)
    logger.propagate = False #avoid having multiple outputs

    ch = logging.StreamHandler()
    if debugConsole:
        ch.setLevel(logging.DEBUG)
    else:
        ch.setLevel(logging.INFO)
    ch.setFormatter(CustomFormatterConsole())
    logger.addHandler(ch)

    # uncomment below to add back file logs
    # if not os.path.exists("logs/"): os.mkdir("logs/")

    # now = datetime.now()
    # dt_string = now.strftime("%d-%m-%Y_%H.%M.%S")

    # ch = logging.FileHandler(f"logs/{dt_string}.log")
    # ch.setLevel(logging.DEBUG)
    # ch.setFormatter(CustomFormatterFile())
    # logger.addHandler(ch)

    return logger

class COLORS:
    pink = "\033[95m"
    blue = "\033[94m"
    cyan = "\033[96m"
    green = "\033[92m"
    grey = "\x1b[38;21m"
    yellow = "\033[93m"
    red = "\033[91m"
    bold = "\033[1m"
    underline = "\033[4m"
    reset = "\033[0m"

#using format instead of strings bc otherwise vscode removes color for everything else
format1 = "%(asctime)s [%(levelname)s] {}%(filename)s:%(lineno)s{} ".format(COLORS.underline, COLORS.reset)
format2 = "%(message)s"

def _get_correctly(prefix: str) -> str:
    return prefix + format1 + prefix + format2 + COLORS.reset

class CustomFormatterConsole(logging.Formatter):
    FORMATS = {
        logging.DEBUG: _get_correctly(COLORS.grey),
        logging.INFO: _get_correctly(COLORS.cyan),
        logging.WARNING: _get_correctly(COLORS.yellow),
        logging.ERROR: _get_correctly(COLORS.red),
        logging.CRITICAL: _get_correctly(COLORS.green) # used as a "success" print
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record).replace(".py", "")

class CustomFormatterFile(logging.Formatter):
    format_ = "%(asctime)s [%(levelname)s] %(filename)s:%(lineno)s %(message)s"

    def format(self, record):
        formatter = logging.Formatter(self.format_)
        return formatter.format(record).replace(".py", "")

#thanks https://stackoverflow.com/a/56944275 & https://stackoverflow.com/a/287944