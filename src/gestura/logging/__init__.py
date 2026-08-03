import logging as _logging

from .root_logger import GesturaLogger

_logger = _logging.getLogger(GesturaLogger.NAME)

setup = GesturaLogger.setup

debug = _logger.debug
info = _logger.info
warning = _logger.warning
error = _logger.error
critical = _logger.critical

exception = _logger.exception
