import logging
import logging.handlers
import os
import sys

import cherrypy

from team_not_found import platform_helper


class ReverseLevelFilter(object):
    """
    Filters log records based on level but in the opposite direction
    to the built-in setLevel().
    Only logs of the specified level or a less serious level are
    allowed.
    """
    def __init__(self, level):
        self._level = level

    def filter(self, record):
        return record.levelno <= self._level


def configure_logging(logging_config):
    """
    Configure all the logging for the CherryPy application
    """
    # Turn off the built-in CherryPy log config that streams logs to stdout and stderr
    # This lets us control everything through the root logger in a consistent way
    cherrypy.log.screen = False

    # Prevent the logger from raising exceptions
    # primarily to reduce the fallout of Python issue 4749
    # See: http://www.cherrypy.org/ticket/646
    logging.raiseExceptions = 0

    root_logger = logging.getLogger()

    # Set the logging level on the root logger (effectively a global filter)
    log_level = getattr(logging, logging_config['log_level'].upper(), logging.DEBUG)
    root_logger.setLevel(log_level)

    # Create a formatter that can be used by the various log handlers
    log_format = '%(levelname)s::%(asctime)s::%(filename)s [%(lineno)d]\t%(message)s'
    if platform_helper.WIN32:
        # Hack the correct line ending for logs in Windows
        # \n is always added by StreamHandler
        log_format += '\r'
    log_formatter = logging.Formatter(log_format)

    if 'log_folder' in logging_config:
        # Make sure log folder exists
        log_folder = os.path.expandvars(logging_config['log_folder'])
        if not os.path.exists(log_folder):
            os.makedirs(log_folder)

        # Always hook the rotating file handler into the root logger
        log_file = os.path.join(log_folder, logging_config['log_file'])
        try:
            rollover_log = logging.handlers.RotatingFileHandler(
                log_file,
                maxBytes=logging_config['log_file_size'] * 1024 * 1024,
                backupCount=5
            )
            rollover_log.setLevel(log_level)
            rollover_log.setFormatter(log_formatter)
            root_logger.addHandler(rollover_log)
        except IOError as ex:
            print 'Unable to write to rotating logfile %s' % log_file
            print unicode(ex).encode('ascii', errors='replace')
            sys.exit(1)

    # If this is not running daemonized (or as a service) then also
    # log to the terminal
    if logging_config['log_to_console']:
        # Create a stream handler to pass all non-errors to stdout
        stdout_handler = logging.StreamHandler(sys.stdout)
        stdout_handler.addFilter(ReverseLevelFilter(logging.WARNING))
        stdout_handler.setFormatter(log_formatter)
        root_logger.addHandler(stdout_handler)

        # Create a stream handler to pass all errors to stderr
        stderr_handler = logging.StreamHandler(sys.stderr)
        stderr_handler.setLevel(logging.ERROR)
        stderr_handler.setFormatter(log_formatter)
        root_logger.addHandler(stderr_handler)

    # Access logging
    cherrypy.log.access_log.propagate = logging_config['access_logging_enabled']

    # Disabled loggers
    for dl in logging_config['disabled_loggers']:
        logging.getLogger(dl).propagate = False
