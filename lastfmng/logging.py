# -*- coding: utf-8 -*-
import logging

from picard import log as picard_log


class PicardHandler(logging.Handler):
    def emit(self, record):
        levels = {
            10: logging.DEBUG,
            20: logging.INFO,
            30: logging.WARNING,
            40: logging.ERROR,
            50: logging.ERROR,
        }
        level = levels.get(record.levelno, logging.DEBUG)
        message = '{} - {}'.format('Last.fm.ng', record.msg)


def setup_logging():
    log = logging.getLogger()
    log.setLevel(0)
    log.addHandler(PicardHandler())
