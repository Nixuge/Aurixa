# TODO: add option to regen GPG keys (prolly)

from update import update_tweaks

def main():
    logging.info("Welcome to Aurixa's CLI")
    if not is_setup():
        logging.info("Looks like you haven't done the setup for your repo. Starting it.")
        setup()
        if "y" not in log_input("Do you want to process your tweaks now? (y/n): ").lower():
            return

    update_tweaks()

if __name__ == "__main__":
    import logging
    from setup import is_setup, setup
    from utils.input import log_input
    from utils.logger import load_proper_logger
    load_proper_logger(logging.getLogger(), True)

    main()
else:
    print("Please run this as a standalone, don't import it.")