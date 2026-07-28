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
Locale = Literal[
    "en",
    "ja",
    "zh-Hans",
    "zh-Hant",
    "es",
    "pt-BR",
    "fr",
    "de",
    "ko",
    "ru",
    "ar",
    "hi",
]
SUPPORTED_LOCALES: tuple[Locale, ...] = (
    "en",
    "ja",
    "zh-Hans",
    "zh-Hant",
    "es",
    "pt-BR",
    "fr",
    "de",
    "ko",
    "ru",
    "ar",
    "hi",
)
_PEANO_HANDLER_MARKER = "_peano_handler"
_LOG_LIMIT_NOTICE = "_peano_log_limit_notice"
_locale: Locale = "en"

_MESSAGES: dict[Locale, dict[str, str]] = {
    "en": {
        "equality.zero": "[equality: zero case]",
        "equality.successor": "[equality: successor case]",
        "addition.base": "[addition: base]",
        "addition.recursive": "[addition: recursive]",
        "multiplication.base": "[multiplication: base]",
        "multiplication.recursive": "[multiplication: recursive]",
        "truncated": (
            "…Log output was truncated after {max_lines} lines. "
            "Use smaller inputs and run the cell again."
        ),
        "midpoint_root": "{polynomial}: midpoint {midpoint} is a root",
    },
    "ja": {
        "equality.zero": "[等値・0の場合]",
        "equality.successor": "[等値・後者の場合]",
        "addition.base": "[加法・基底]",
        "addition.recursive": "[加法・再帰]",
        "multiplication.base": "[乗法・基底]",
        "multiplication.recursive": "[乗法・再帰]",
        "truncated": (
            "…ログは{max_lines}行で省略しました。入力を小さくして再実行してください。"
        ),
        "midpoint_root": "{polynomial}: 中点 {midpoint} は根",
    },
    "zh-Hans": {
        "equality.zero": "[相等：零情形]",
        "equality.successor": "[相等：后继情形]",
        "addition.base": "[加法：基础情形]",
        "addition.recursive": "[加法：递归情形]",
        "multiplication.base": "[乘法：基础情形]",
        "multiplication.recursive": "[乘法：递归情形]",
        "truncated": "…日志在{max_lines}行后截断。请减小输入后重新运行。",
        "midpoint_root": "{polynomial}：中点 {midpoint} 是根",
    },
    "zh-Hant": {
        "equality.zero": "[相等：零情形]",
        "equality.successor": "[相等：後繼情形]",
        "addition.base": "[加法：基礎情形]",
        "addition.recursive": "[加法：遞迴情形]",
        "multiplication.base": "[乘法：基礎情形]",
        "multiplication.recursive": "[乘法：遞迴情形]",
        "truncated": "…記錄在{max_lines}行後截斷。請縮小輸入後重新執行。",
        "midpoint_root": "{polynomial}：中點 {midpoint} 是根",
    },
    "es": {
        "equality.zero": "[igualdad: caso cero]",
        "equality.successor": "[igualdad: caso sucesor]",
        "addition.base": "[suma: caso base]",
        "addition.recursive": "[suma: caso recursivo]",
        "multiplication.base": "[multiplicación: caso base]",
        "multiplication.recursive": "[multiplicación: caso recursivo]",
        "truncated": (
            "…El registro se truncó tras {max_lines} líneas. "
            "Reduce la entrada y vuelve a ejecutar."
        ),
        "midpoint_root": "{polynomial}: el punto medio {midpoint} es una raíz",
    },
    "pt-BR": {
        "equality.zero": "[igualdade: caso zero]",
        "equality.successor": "[igualdade: caso sucessor]",
        "addition.base": "[adição: caso base]",
        "addition.recursive": "[adição: caso recursivo]",
        "multiplication.base": "[multiplicação: caso base]",
        "multiplication.recursive": "[multiplicação: caso recursivo]",
        "truncated": (
            "…O log foi truncado após {max_lines} linhas. "
            "Reduza a entrada e execute novamente."
        ),
        "midpoint_root": "{polynomial}: o ponto médio {midpoint} é uma raiz",
    },
    "fr": {
        "equality.zero": "[égalité : cas zéro]",
        "equality.successor": "[égalité : cas successeur]",
        "addition.base": "[addition : cas de base]",
        "addition.recursive": "[addition : cas récursif]",
        "multiplication.base": "[multiplication : cas de base]",
        "multiplication.recursive": "[multiplication : cas récursif]",
        "truncated": (
            "…Le journal a été tronqué après {max_lines} lignes. "
            "Réduisez les entrées et relancez."
        ),
        "midpoint_root": "{polynomial} : le milieu {midpoint} est une racine",
    },
    "de": {
        "equality.zero": "[Gleichheit: Nullfall]",
        "equality.successor": "[Gleichheit: Nachfolgerfall]",
        "addition.base": "[Addition: Basisfall]",
        "addition.recursive": "[Addition: Rekursionsfall]",
        "multiplication.base": "[Multiplikation: Basisfall]",
        "multiplication.recursive": "[Multiplikation: Rekursionsfall]",
        "truncated": (
            "…Die Protokollausgabe wurde nach {max_lines} Zeilen gekürzt. "
            "Verkleinern Sie die Eingaben und führen Sie die Zelle erneut aus."
        ),
        "midpoint_root": "{polynomial}: Der Mittelpunkt {midpoint} ist eine Nullstelle",
    },
    "ko": {
        "equality.zero": "[같음: 0인 경우]",
        "equality.successor": "[같음: 후속자 경우]",
        "addition.base": "[덧셈: 기저 경우]",
        "addition.recursive": "[덧셈: 재귀 경우]",
        "multiplication.base": "[곱셈: 기저 경우]",
        "multiplication.recursive": "[곱셈: 재귀 경우]",
        "truncated": (
            "…로그를 {max_lines}줄에서 줄였습니다. 입력을 작게 바꾸고 다시 실행하세요."
        ),
        "midpoint_root": "{polynomial}: 중점 {midpoint}은(는) 근입니다",
    },
    "ru": {
        "equality.zero": "[равенство: случай нуля]",
        "equality.successor": "[равенство: случай следующего]",
        "addition.base": "[сложение: базовый случай]",
        "addition.recursive": "[сложение: рекурсивный случай]",
        "multiplication.base": "[умножение: базовый случай]",
        "multiplication.recursive": "[умножение: рекурсивный случай]",
        "truncated": (
            "…Журнал обрезан после {max_lines} строк. "
            "Уменьшите входные данные и запустите ячейку снова."
        ),
        "midpoint_root": "{polynomial}: середина {midpoint} является корнем",
    },
    "ar": {
        "equality.zero": "[المساواة: حالة الصفر]",
        "equality.successor": "[المساواة: حالة الخليفة]",
        "addition.base": "[الجمع: الحالة الأساسية]",
        "addition.recursive": "[الجمع: الحالة العودية]",
        "multiplication.base": "[الضرب: الحالة الأساسية]",
        "multiplication.recursive": "[الضرب: الحالة العودية]",
        "truncated": (
            "…اختُصر السجل بعد {max_lines} سطرًا. صغّر المدخلات ثم شغّل الخلية من جديد."
        ),
        "midpoint_root": "{polynomial}: نقطة المنتصف {midpoint} جذر",
    },
    "hi": {
        "equality.zero": "[समानता: शून्य स्थिति]",
        "equality.successor": "[समानता: उत्तराधिकारी स्थिति]",
        "addition.base": "[जोड़: आधार स्थिति]",
        "addition.recursive": "[जोड़: पुनरावर्ती स्थिति]",
        "multiplication.base": "[गुणा: आधार स्थिति]",
        "multiplication.recursive": "[गुणा: पुनरावर्ती स्थिति]",
        "truncated": (
            "…लॉग {max_lines} पंक्तियों के बाद छोटा कर दिया गया। इनपुट घटाकर सेल फिर चलाएँ।"
        ),
        "midpoint_root": "{polynomial}: मध्यबिंदु {midpoint} एक मूल है",
    },
}


def translate(key: str, **values: object) -> str:
    """Return a runtime message in the configured locale."""

    return _MESSAGES[_locale][key].format(**values)


def localized(english: str, japanese: str) -> str:
    """Return an English/Japanese compatibility message.

    New runtime messages should use :func:`translate`.
    """
    return japanese if _locale == "ja" else english


class _LineLimitFormatter(Formatter):
    """Format a copied record when emitting the truncation notice."""

    def format(self, record: LogRecord) -> str:
        max_lines = getattr(record, _LOG_LIMIT_NOTICE, None)
        if not isinstance(max_lines, int):
            return super().format(record)
        notice = copy(record)
        notice.msg = translate("truncated", max_lines=max_lines)
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
    locale: Locale = "en",
) -> None:
    """Write symbolic evaluation logs to standard error.

    By default, only the library logger is configured. ``root=True`` preserves
    existing root handlers and manages only the handler installed here.
    ``max_lines`` emits one truncation notice after the limit. Pass
    ``"Level %(levelno)s: %(message)s"`` as ``fmt`` to expose internal levels.
    Runtime labels are English by default. ``SUPPORTED_LOCALES`` lists the
    available translations.
    """

    global _locale
    if max_lines is not None and (
        isinstance(max_lines, bool) or not isinstance(max_lines, int) or max_lines < 1
    ):
        raise ValueError("max_lines must be a positive integer or None")
    if locale not in SUPPORTED_LOCALES:
        supported = ", ".join(SUPPORTED_LOCALES)
        raise ValueError(f"locale must be one of: {supported}")
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
