import io
import logging
import unittest
from contextlib import redirect_stderr
from inspect import signature
from typing import get_type_hints

import peano.utils as peano_utils
from peano import N_ONE, NaturalNumber, natural_number
from peano.utils import LogMessage, config_log, log, logger


class TestLogging(unittest.TestCase):
    def setUp(self) -> None:
        self.root_logger = logging.getLogger()
        self.original_root_handlers = list(self.root_logger.handlers)
        self.original_module_handlers = list(logger.handlers)
        self.original_propagate = logger.propagate
        self.original_level = logger.level
        self.original_disabled = logger.disabled
        self.original_locale = peano_utils._locale

    def tearDown(self) -> None:
        self.root_logger.handlers[:] = self.original_root_handlers
        logger.handlers[:] = self.original_module_handlers
        logger.propagate = self.original_propagate
        logger.setLevel(self.original_level)
        logger.disabled = self.original_disabled
        peano_utils._locale = self.original_locale

    def test_default_configuration_does_not_propagate_or_duplicate(self) -> None:
        root_stream = io.StringIO()
        self.root_logger.handlers[:] = [logging.StreamHandler(root_stream)]
        logger.handlers.clear()

        own_stream = io.StringIO()
        with redirect_stderr(own_stream):
            config_log(log_level=4)
            N_ONE + N_ONE

        self.assertEqual(root_stream.getvalue(), "")
        self.assertEqual(len(own_stream.getvalue().splitlines()), 2)

    def test_addition_trace_names_rules_and_uses_structural_notation(self) -> None:
        own_stream = io.StringIO()
        with redirect_stderr(own_stream):
            config_log(log_level=4)
            natural_number(2) + natural_number(2)

        self.assertEqual(
            own_stream.getvalue().splitlines(),
            [
                "[addition: base] add(S(S(0)), 0) -> S(S(0))",
                "[addition: recursive] add(S(S(0)), S(0)) -> S(add(S(S(0)), 0))",
                "[addition: recursive] add(S(S(0)), S(S(0))) -> S(add(S(S(0)), S(0)))",
            ],
        )

    def test_equality_trace_names_axiom_cases(self) -> None:
        own_stream = io.StringIO()
        with redirect_stderr(own_stream):
            config_log(log_level=1)
            natural_number(2) == natural_number(1)

        self.assertEqual(
            own_stream.getvalue().splitlines(),
            [
                "[equality: zero case] eq(S(0), 0) -> False",
                "[equality: successor case] eq(S(S(0)), S(0)) -> eq(S(0), 0)",
            ],
        )

    def test_log_level_can_be_shown_with_an_explicit_format(self) -> None:
        own_stream = io.StringIO()
        with redirect_stderr(own_stream):
            config_log(
                log_level=4,
                fmt="Level %(levelno)s: %(message)s",
            )
            N_ONE + N_ONE

        self.assertEqual(
            own_stream.getvalue().splitlines(),
            [
                "Level 4: [addition: base] add(S(0), 0) -> S(0)",
                "Level 4: [addition: recursive] add(S(0), S(0)) -> S(add(S(0), 0))",
            ],
        )

    def test_root_configuration_preserves_host_handlers(self) -> None:
        host_handler = logging.StreamHandler(io.StringIO())
        self.root_logger.handlers[:] = [host_handler]
        logger.handlers.clear()

        config_log(log_level=4, root=True)

        self.assertIn(host_handler, self.root_logger.handlers)
        self.assertEqual(len(self.root_logger.handlers), 2)

    def test_reconfiguration_replaces_only_peano_handler(self) -> None:
        host_handler = logging.StreamHandler(io.StringIO())
        self.root_logger.handlers[:] = [host_handler]
        logger.handlers.clear()

        config_log(log_level=4, root=True)
        config_log(log_level=4, root=False)

        self.assertEqual(self.root_logger.handlers, [host_handler])
        self.assertEqual(len(logger.handlers), 1)
        self.assertFalse(logger.propagate)

    def test_decorator_preserves_method_metadata(self) -> None:
        self.assertEqual(N_ONE.__add__.__name__, "__add__")
        self.assertTrue(hasattr(N_ONE.__add__, "__wrapped__"))
        self.assertEqual(signature(N_ONE.__add__).return_annotation, "NaturalNumber")
        self.assertIs(get_type_hints(N_ONE.__add__)["return"], NaturalNumber)

    def test_decorator_exposes_the_result_annotation(self) -> None:
        @log(log_level=1)
        def example() -> tuple[int, str]:
            return 1, "one"

        self.assertIs(signature(example).return_annotation, int)
        self.assertIs(get_type_hints(example)["return"], int)

    def test_lazy_message_is_only_rendered_when_log_is_enabled(self) -> None:
        render_count = 0

        def render() -> str:
            nonlocal render_count
            render_count += 1
            return "rendered"

        @log(log_level=41)
        def example() -> tuple[int, LogMessage]:
            return 1, render

        logger.handlers.clear()
        logger.disabled = True
        self.assertEqual(example(), 1)
        self.assertEqual(render_count, 0)

        stream = io.StringIO()
        with redirect_stderr(stream):
            config_log(log_level=4)
            self.assertEqual(example(), 1)

        self.assertEqual(render_count, 1)
        self.assertIn("rendered", stream.getvalue())

    def test_log_line_limit_emits_one_truncation_notice(self) -> None:
        stream = io.StringIO()
        with redirect_stderr(stream):
            config_log(log_level=4, max_lines=2)
            natural_number(1) + natural_number(2)

        lines = stream.getvalue().splitlines()
        self.assertEqual(len(lines), 3)
        self.assertIn("truncated after 2 lines", lines[-1])

    def test_japanese_runtime_labels_are_opt_in(self) -> None:
        stream = io.StringIO()
        with redirect_stderr(stream):
            config_log(log_level=4, max_lines=1, locale="ja")
            natural_number(1) + natural_number(1)

        self.assertEqual(
            stream.getvalue().splitlines(),
            [
                "[加法・基底] add(S(0), 0) -> S(0)",
                "…ログは1行で省略しました。入力を小さくして再実行してください。",
            ],
        )

    def test_log_line_limit_must_be_positive(self) -> None:
        with self.assertRaises(ValueError):
            config_log(max_lines=0)

    def test_locale_must_be_supported(self) -> None:
        with self.assertRaises(ValueError):
            config_log(locale="fr")  # ty: ignore[invalid-argument-type]


if __name__ == "__main__":
    unittest.main()
