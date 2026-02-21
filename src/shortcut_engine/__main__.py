import logging
from .utils.logger_setup import RootLogger
from .examples.run import main

RootLogger.setup(level=logging.INFO)
_main = main()
_main.start()
