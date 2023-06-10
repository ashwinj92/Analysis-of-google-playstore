from termcolor import colored


class Console:
    @staticmethod
    def log(message: str) -> None:
        print(message)

    @staticmethod
    def log_error(message: str) -> None:
        print(colored(message, 'red'))

    @staticmethod
    def log_info(message: str) -> None:
        print(colored(message, 'green'))
