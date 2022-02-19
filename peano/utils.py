from logging import Formatter, StreamHandler, getLogger
from typing import Any, Callable, TypeVar

logger = getLogger(__name__)


T = TypeVar("T")


def log(log_level: int) -> Callable[..., Callable[..., Any]]:
    def outer(func: Callable[..., tuple[T, str]]) -> Callable[..., T]:
        def inner(*args: Any, **kwargs: Any) -> T:
            result, message = func(*args, **kwargs)
            logger.log(log_level, message)
            return result

        return inner

    return outer


def config_log(
    log_level: int = 0,
    root: bool = False,
    fmt: str = "Level %(levelno)s: %(message)s",
    clear_handlers: bool = True,
) -> None:
    logger = getLogger(None if root else __name__)
    if clear_handlers:
        logger.handlers.clear()
    handler = StreamHandler()
    handler.setFormatter(Formatter(fmt))
    logger.addHandler(handler)
    logger.setLevel(log_level)
