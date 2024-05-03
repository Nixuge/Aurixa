import logging

def log_input(data: str) -> str:
    """
    Same function as input(), except it uses loggging to ask you the question
    """
    logging.info(data)
    return input()

def blank_log_input(data: str) -> str | None:
    """
    Same function as input(), except:
    - it uses loggging to ask you the question
    - if the given string is "", it'll return "None"
    """
    res = log_input(data)
    if res == "":
        return None
    return res
