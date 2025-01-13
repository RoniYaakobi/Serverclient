from clock import Clock

class Shortcut:
    """
    Includes all the constants and QOL commands I am using in my code. Basically a bunch of flags.
    """
    ACTIVE = True
    INACTIVE = False

    RUNNING = True

    RED = "\033[38;5;196m"
    GREEN = "\033[38;5;47m"
    YELLOW = "\033[38;5;227m"
    CYAN = "\033[38;5;51m"

    RESET = "\033[0m"
    
    # Logging functionality TODO add file logging too.
    @staticmethod
    def print_color(msg,color , clock = True):
        # format the message to go to the log and cmd log.
        print(f"{color}{msg} {f"({Clock.get_date_time()})" if clock else ""}{Shortcut.RESET}")
    
    @staticmethod
    def print_error(msg , clock = True):
        Shortcut.print_color(msg, Shortcut.RED, clock)

    @staticmethod
    def print_warning(msg , clock = True):
        Shortcut.print_color(msg, Shortcut.YELLOW, clock)

    @staticmethod
    def print_success(msg , clock = True):
        Shortcut.print_color(msg, Shortcut.GREEN, clock)

    @staticmethod
    def print_initializing(msg , clock = True):
        Shortcut.print_color(msg, Shortcut.CYAN, clock)


