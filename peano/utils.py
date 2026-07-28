"""Lightweight logging support for observing symbolic evaluation."""

from copy import copy
from functools import wraps
from inspect import signature
from logging import (
    Filter,
    Formatter,
    Logger,
    LogRecord,
    NullHandler,
    StreamHandler,
    getLogger,
)
from typing import Callable, Literal, ParamSpec, TypeVar, get_args, get_origin

logger = getLogger(__name__)
logger.addHandler(NullHandler())
logger.propagate = False
logger.disabled = True

P = ParamSpec("P")
T = TypeVar("T")
LogMessage = str | Callable[[], str]
_PEANO_HANDLER_MARKER = "_peano_handler"
_LOG_LIMIT_NOTICE = "_peano_log_limit_notice"
_locale: Literal["en", "ja"] = "en"


def localized(english: str, japanese: str) -> str:
    """Return a localized runtime message."""

    return japanese if _locale == "ja" else english


class _LineLimitFormatter(Formatter):
    """Format a copied record when emitting the truncation notice."""

    def format(self, record: LogRecord) -> str:
        max_lines = getattr(record, _LOG_LIMIT_NOTICE, None)
        if not isinstance(max_lines, int):
            return super().format(record)
        notice = copy(record)
        notice.msg = localized(
            f"…Log output was truncated after {max_lines} lines. "
            "Use smaller inputs and run the cell again.",
            f"…ログは{max_lines}行で省略しました。入力を小さくして再実行してください。",
        )
        notice.args = ()
        return super().format(notice)


class _LineLimitFilter(Filter):
    """Emit at most ``max_lines`` messages plus one truncation notice."""

    def __init__(self, max_lines: int | None) -> None:
        super().__init__(__name__)
        self.max_lines = max_lines
        self.emitted_lines = 0

    def filter(self, record: LogRecord) -> bool:
        if not super().filter(record):
            return False
        if self.max_lines is None:
            return True
        if self.emitted_lines < self.max_lines:
            self.emitted_lines += 1
            return True
        if self.emitted_lines == self.max_lines:
            self.emitted_lines += 1
            setattr(record, _LOG_LIMIT_NOTICE, self.max_lines)
            return True
        return False


def log(
    log_level: int,
) -> Callable[[Callable[P, tuple[T, LogMessage]]], Callable[P, T]]:
    """Turn an operation returning a result and message into a public operation.

    The implementation returns ``(result, formula)``. Callers receive only
    ``result`` while ``formula`` is logged at the requested level. Callable
    messages are evaluated lazily only when logging is enabled.
    """

    def outer(func: Callable[P, tuple[T, LogMessage]]) -> Callable[P, T]:
        @wraps(func)
        def inner(*args: P.args, **kwargs: P.kwargs) -> T:
            result, message = func(*args, **kwargs)
            if logger.isEnabledFor(log_level):
                logger.log(
                    log_level, message if isinstance(message, str) else message()
                )
            return result

        public_return = _public_return_annotation(
            signature(func, follow_wrapped=False).return_annotation
        )
        inner.__annotations__ = {
            **func.__annotations__,
            "return": public_return,
        }
        setattr(
            inner,
            "__signature__",
            signature(func, follow_wrapped=False).replace(
                return_annotation=public_return
            ),
        )
        return inner

    return outer


def _public_return_annotation(annotation: object) -> object:
    """Extract the public result type from the internal tuple annotation."""

    if isinstance(annotation, str):
        prefix = "tuple["
        for suffix in (", str]", ", LogMessage]"):
            if annotation.startswith(prefix) and annotation.endswith(suffix):
                return annotation[len(prefix) : -len(suffix)]
    elif get_origin(annotation) is tuple:
        arguments = get_args(annotation)
        if len(arguments) == 2 and arguments[1] in (str, LogMessage):
            return arguments[0]
    raise TypeError("functions decorated with log must return (result, LogMessage)")


def _remove_peano_handlers(*loggers: Logger) -> None:
    """Remove only handlers installed by this module."""

    for target in loggers:
        for handler in tuple(target.handlers):
            if getattr(handler, _PEANO_HANDLER_MARKER, False):
                target.removeHandler(handler)
                handler.close()


def config_log(
    log_level: int = 0,
    root: bool = False,
    fmt: str = "%(message)s",
    clear_handlers: bool = True,
    max_lines: int | None = None,
    locale: Literal["en", "ja"] = "en",
) -> None:
    """Write symbolic evaluation logs to standard error.

    By default, only the library logger is configured. ``root=True`` preserves
    existing root handlers and manages only the handler installed here.
    ``max_lines`` emits one truncation notice after the limit. Pass
    ``"Level %(levelno)s: %(message)s"`` as ``fmt`` to expose internal levels.
    Runtime labels are English by default; ``locale="ja"`` selects Japanese.
    """

    global _locale
    if max_lines is not None and (
        isinstance(max_lines, bool) or not isinstance(max_lines, int) or max_lines < 1
    ):
        raise ValueError("max_lines must be a positive integer or None")
    if locale not in ("en", "ja"):
        raise ValueError("locale must be 'en' or 'ja'")
    _locale = locale

    root_logger = getLogger()
    if clear_handlers:
        _remove_peano_handlers(logger, root_logger)

    handler = StreamHandler()
    handler.setFormatter(_LineLimitFormatter(fmt))
    handler.setLevel(log_level)
    handler.addFilter(_LineLimitFilter(max_lines))
    setattr(handler, _PEANO_HANDLER_MARKER, True)

    logger.setLevel(log_level)
    logger.disabled = False
    if root:
        logger.propagate = True
        root_logger.addHandler(handler)
    else:
        logger.propagate = False
        logger.addHandler(handler)


def explain(value: object) -> str:
    """Render a value consistently inside symbolic log messages."""

    return repr(value)
