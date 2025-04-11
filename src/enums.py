from enum import StrEnum


class Run_Modes(StrEnum):
    prod = "PROD"
    dev = "DEV"

class LogLevels(StrEnum):
    info = "INFO"
    warn = "WARN"
    error = "ERROR"
    debug = "DEBUG"