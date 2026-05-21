from __future__ import annotations


class ForgeToolError(Exception):
    def __init__(self, message: str, *, transient: bool = False) -> None:
        super().__init__(message)
        self.transient = transient


class TransientToolError(ForgeToolError):
    def __init__(self, message: str) -> None:
        super().__init__(message, transient=True)


class PermanentToolError(ForgeToolError):
    def __init__(self, message: str) -> None:
        super().__init__(message, transient=False)


class OutputValidationError(ForgeToolError):
    def __init__(self, message: str, *, transient: bool = False) -> None:
        super().__init__(message, transient=transient)


def is_transient_error(exc: Exception) -> bool:
    if isinstance(exc, ForgeToolError):
        return bool(getattr(exc, "transient", False))
    return isinstance(exc, (TimeoutError, ConnectionError))
