from typing import Optional


class CommonException(Exception):
    """
    Base Exception
    """
    message: str

    def __init__(self, message: Optional[str] = None) -> None:
        self._message = message

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}: {self.message}'


class ConfigurationError(CommonException):
    """Exception raised for errors in Config dataclass.

    Attributes:
        message -- explanation of the error
    """
