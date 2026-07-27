"""式変形を観察するための軽量なログ基盤。"""

from functools import wraps
from logging import (
    Filter,
    Formatter,
    Logger,
    NullHandler,
    StreamHandler,
    getLogger,
)
from typing import Any, Callable, ParamSpec, TypeVar

logger = getLogger(__name__)
logger.addHandler(NullHandler())
logger.propagate = False

P = ParamSpec("P")
T = TypeVar("T")
_PEANO_HANDLER_MARKER = "_peano_handler"


def log(log_level: int) -> Callable[[Callable[P, tuple[T, str]]], Callable[P, T]]:
    """計算結果と説明文を返す関数を、通常の演算へ変換する。

    演算本体は ``(result, formula)`` を返す。利用者には ``result`` だけを返し、
    ``formula`` は指定レベルで記録する。この分離により、数学的な定義と
    Python の演算子インターフェースを同時に保てる。
    """

    def outer(func: Callable[P, tuple[T, str]]) -> Callable[P, T]:
        @wraps(func)
        def inner(*args: P.args, **kwargs: P.kwargs) -> T:
            result, message = func(*args, **kwargs)
            logger.log(log_level, message)
            return result

        return inner

    return outer


def _remove_peano_handlers(*loggers: Logger) -> None:
    """このモジュールが追加した handler だけを取り除く。"""

    for target in loggers:
        for handler in tuple(target.handlers):
            if getattr(handler, _PEANO_HANDLER_MARKER, False):
                target.removeHandler(handler)
                handler.close()


def config_log(
    log_level: int = 0,
    root: bool = False,
    fmt: str = "Level %(levelno)s: %(message)s",
    clear_handlers: bool = True,
) -> None:
    """式変形ログを標準エラーへ出力する。

    通常はこのライブラリ専用ロガーだけを設定する。``root=True`` でも
    既存の root handler は保持し、この関数が追加した handler だけを管理する。
    """

    root_logger = getLogger()
    if clear_handlers:
        _remove_peano_handlers(logger, root_logger)

    handler = StreamHandler()
    handler.setFormatter(Formatter(fmt))
    handler.setLevel(log_level)
    handler.addFilter(Filter(__name__))
    setattr(handler, _PEANO_HANDLER_MARKER, True)

    logger.setLevel(log_level)
    if root:
        logger.propagate = True
        root_logger.addHandler(handler)
    else:
        logger.propagate = False
        logger.addHandler(handler)


def explain(value: Any) -> str:
    """ログ式中で値を一貫して表示する。"""

    return repr(value)
