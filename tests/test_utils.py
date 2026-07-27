import io
import logging
import unittest
from contextlib import redirect_stderr

from peano import N_ONE
from peano.utils import config_log, logger


class TestLogging(unittest.TestCase):
    def setUp(self) -> None:
        self.root_logger = logging.getLogger()
        self.original_root_handlers = list(self.root_logger.handlers)
        self.original_module_handlers = list(logger.handlers)
        self.original_propagate = logger.propagate
        self.original_level = logger.level

    def tearDown(self) -> None:
        self.root_logger.handlers[:] = self.original_root_handlers
        logger.handlers[:] = self.original_module_handlers
        logger.propagate = self.original_propagate
        logger.setLevel(self.original_level)

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


if __name__ == "__main__":
    unittest.main()
