import os
import sys
import datetime
from logging import Logger, StreamHandler, Formatter, FileHandler
#from typing import Self
from typing_extensions import Self
from pathlib import Path


class CustomLogger(Logger):
    """Custom logger class that support logging to both the console and local file.
    """
    _instance = None

    def __new__(cls, *args, **kwargs) -> Self:
        """Return the existing instance if it exists, otherwise create a new one."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            
        return cls._instance
    
    def __init__(
            self, 
            *args,
            name: str = 'custom_logger', 
            level: str = "INFO",
            write_local: bool = False,
            **kwargs
    ) -> None:
        
        super().__init__(name, level, *args, **kwargs)
        self._log_file_name = self.log_file_name
        self._add_stream_handler()

        if write_local:
            self._add_file_handler()

    @property    
    def log_file_name(self) -> str:
        """Return a file name for the log file"""
        return datetime.datetime.now().strftime("%Y%m%d_%H%M%S") + ".log"
    
    def _add_stream_handler(self) -> None:
        """Add stream handler to stream logging message to the console"""
        stream_handler = StreamHandler(stream=sys.stderr)
        stream_format = Formatter("%(asctime)s:%(name)s:%(levelname)s:%(message)s")
        stream_handler.setFormatter(stream_format)
        self.addHandler(stream_handler)

    def _add_file_handler(self) -> None:
        """Add file handler to write log to local file"""
        log_path = Path(__file__).resolve().parents[1].joinpath("logs")
        if not os.path.exists(log_path):
            os.makedirs(log_path)

        file_handler = FileHandler(
            filename=os.path.join(log_path, self.log_file_name)
        )
        file_format = Formatter(
            "%(asctime)s:%(name)s:%(levelname)s:%(message)s"
        )
        file_handler.setFormatter(file_format)
        self.addHandler(file_handler)

    
