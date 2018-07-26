#!/usr/bin/env python

""" This module contains custom filters used by AutoBot module """
import logging

from telegram.ext import BaseFilter

class IdFilter(BaseFilter):
    """ Custum filter class that allow only specified ID to interact with this bot """

    def __init__(self, restrict, allowed):
        self._logger = logging.getLogger(__name__)
        self._allowed = allowed
        self._restrict = restrict

    def filter(self, message):
        if not (self._restrict and (message.chat.id in self._allowed)):
            self._logger.warning('Id filtering rejects a message from: %i', message.chat.id)
            return False
        else:
            return True
