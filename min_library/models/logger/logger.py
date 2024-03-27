import inspect
import logging
import os
import sys
from pathlib import Path

from min_library.models.others.constants import LogStatus


class CustomLogger:
    FOLDER_NAME: str = 'user_data/logs'
    LOGGERS: dict[str, logging.Logger] = {}

    def __init__(
        self,
        account_id: str | int,
        address: str,
        network: str,
        create_log_file_per_account: bool = False
    ) -> None:
        self.account_id = account_id
        self.masked_address = address[:6] + "..." + address[-4:]
        self.network = network
        self.create_log_file_per_account = create_log_file_per_account
        if create_log_file_per_account:
            self._create_log_folder()

    @classmethod
    def _create_log_folder(cls):
        relative_path = Path(cls.FOLDER_NAME)
        relative_path.mkdir(parents=True, exist_ok=True)

    def _initialize_main_log(self) -> logging.Logger:
        if 'main_logger' not in self.LOGGERS:
            name_of_file = "main"

            main_logger = logging.getLogger(name_of_file)
            main_logger.setLevel(logging.DEBUG)

            console_handler = logging.StreamHandler(sys.stderr)
            console_handler.setLevel(logging.INFO)
            console_handler.setFormatter(MainConsoleLogFormatter())
            main_logger.addHandler(console_handler)

            file_handler = logging.FileHandler(f"{name_of_file}.log")
            file_handler.setLevel(logging.INFO)
            file_handler.setFormatter(MainFileLogFormatter())
            main_logger.addHandler(file_handler)

            logging.addLevelName(403, LogStatus.FAILED)
            logging.addLevelName(204, LogStatus.SUCCESS)

            logging.addLevelName(210, LogStatus.APPROVED)
            logging.addLevelName(201, LogStatus.MINTED)
            logging.addLevelName(202, LogStatus.BRIDGED)
            logging.addLevelName(203, LogStatus.SWAPPED)

            self.LOGGERS["main_logger"] = main_logger

        return self.LOGGERS["main_logger"]

    def _initialize_account_log(self, account_id: str) -> logging.Logger:
        if account_id not in self.LOGGERS:
            name_of_file = f'{self.FOLDER_NAME}/log_{account_id}'

            wallet_logger = logging.getLogger(name_of_file)
            file_handler = logging.FileHandler(f"{name_of_file}.log")
            file_handler.setLevel(logging.INFO)
            file_handler.setFormatter(AccountFileLogFormatter())
            wallet_logger.addHandler(file_handler)

            self.LOGGERS[account_id] = wallet_logger

        return self.LOGGERS[account_id]

    def log_message(self, status: str, message: str) -> None:
        caller_frame = inspect.currentframe().f_back
        calling_line = f"{os.path.basename(caller_frame.f_code.co_filename)}:{caller_frame.f_lineno}"

        message_with_calling_line = f"{calling_line:<25} | {message}"
        extra = {
            "account_id": self.account_id,
            "address": self.masked_address,
            "network": self.network
        }

        main_logger = self._initialize_main_log()
        main_logger.log(
            level=logging.getLevelName(status),
            msg=message_with_calling_line,
            extra=extra
        )

        if self.create_log_file_per_account:
            logger = self._initialize_account_log(self.account_id)
            logger.log(
                level=logging.getLevelName(status),
                msg=message_with_calling_line,
                extra=extra
            )


class CustomLogData(logging.Formatter):
    TIME_FORMAT = '%Y-%m-%d %H:%M:%S'

    LOG_TIME_FORMAT = '%(asctime)s |'
    LOG_LEVELNAME_FORMAT = ' %(levelname)-8s '
    LOG_MESSAGE_FORMAT = '| %(account_id)8s | %(address)s | %(network)-12s | %(message)s'
    LOG_MESSAGE_FORMAT_SHORT = '| %(message)s '

    RED = "\x1b[31;20m"
    GREEN = "\x1b[32;20m"
    YELLOW = "\x1b[33;20m"
    BLUE = "\x1b[34;20m"
    WHITE = "\x1b[37;20m"
    GREY = "\x1b[38;20m"
    RESET = "\x1b[0m"

    SUCCESS_FORMAT = GREEN + LOG_LEVELNAME_FORMAT + RESET

    FORMATS = {
        LogStatus.DEBUG: BLUE + LOG_LEVELNAME_FORMAT + RESET,
        LogStatus.INFO: WHITE + LOG_LEVELNAME_FORMAT + RESET,
        LogStatus.WARNING: YELLOW + LOG_LEVELNAME_FORMAT + RESET,
        LogStatus.SUCCESS: SUCCESS_FORMAT,
        LogStatus.ERROR: RED + LOG_LEVELNAME_FORMAT + RESET,
        LogStatus.FAILED: RED + LOG_LEVELNAME_FORMAT + RESET,

        LogStatus.APPROVED: SUCCESS_FORMAT,
        LogStatus.MINTED: SUCCESS_FORMAT,
        LogStatus.BRIDGED: SUCCESS_FORMAT,
        LogStatus.SWAPPED: SUCCESS_FORMAT
    }

    def __init__(self, *args, **kwargs):
        self.root_folder = os.getcwd()
        super().__init__(*args, **kwargs)


class SettingsLogFormatter(CustomLogData):
    def __init__(
        self,
        log_levelname_format: str | dict,
        log_message_format: str,
    ) -> logging.Formatter:
        super().__init__()
        self.log_levelname_format = log_levelname_format
        self.log_message_format = log_message_format

    def format(self, record):
        levelname = record.levelname
        if isinstance(self.log_levelname_format, dict):
            log_levelname_format = self.log_levelname_format[levelname]
        else:
            log_levelname_format = self.log_levelname_format

        if levelname in self.FORMATS:
            formatted_message = self.LOG_TIME_FORMAT + \
                log_levelname_format + self.log_message_format
            formatter = logging.Formatter(
                formatted_message,
                datefmt=self.TIME_FORMAT
            )

        return formatter.format(record)


class MainConsoleLogFormatter(SettingsLogFormatter):
    def __init__(self):
        super().__init__(
            self.FORMATS,
            self.LOG_MESSAGE_FORMAT,
        )

    def format(self, record):
        return super().format(record)


class MainFileLogFormatter(SettingsLogFormatter):
    def __init__(self):
        super().__init__(
            self.LOG_LEVELNAME_FORMAT,
            self.LOG_MESSAGE_FORMAT,
        )

    def format(self, record):
        return super().format(record)


class AccountFileLogFormatter(SettingsLogFormatter):
    def __init__(self):
        super().__init__(
            self.LOG_LEVELNAME_FORMAT,
            self.LOG_MESSAGE_FORMAT,
        )

    def format(self, record):
        return super().format(record)


class CommonConsoleLogFormatter(SettingsLogFormatter):
    def __init__(self):
        super().__init__(
            self.FORMATS,
            self.LOG_MESSAGE_FORMAT_SHORT,
        )

    def format(self, record):
        return super().format(record)


class CommonConsoleFileLogFormatter(SettingsLogFormatter):
    def __init__(self):
        super().__init__(
            self.LOG_LEVELNAME_FORMAT,
            self.LOG_MESSAGE_FORMAT_SHORT,
        )

    def format(self, record):
        return super().format(record)


class ConsoleLoggerSingleton:
    _instance = None

    @staticmethod
    def get_logger():
        if ConsoleLoggerSingleton._instance is None:
            logger = logging.getLogger(__name__)
            logger.setLevel(logging.INFO)

            console_handler = logging.StreamHandler()
            console_handler.setFormatter(CommonConsoleLogFormatter())
            logger.addHandler(console_handler)

            console_handler = logging.FileHandler("main.log")
            console_handler.setFormatter(CommonConsoleFileLogFormatter())
            logger.addHandler(console_handler)
            ConsoleLoggerSingleton._instance = logger

        return ConsoleLoggerSingleton._instance


console_logger = ConsoleLoggerSingleton.get_logger()
