#!/usr/bin/env python

""" This module contains some usefull factory used by AutoBot module """
import logging

from autobot import AutoBotConstants
from autobot.configuration import AutoBotConfig, AutoBotSettings
from autobot.handler.ptb import FilterRegexHandler
from autobot.filters import IdFilter, TextEqualsFilter
from autobot.plugins import PluginsLoader

from telegram.ext import CommandHandler, MessageHandler, ConversationHandler

class CallbackHandlerFactory(object):

    _logger = logging.getLogger(__name__)

    @classmethod
    def build_callback(cls, settings, config, entry):
        if entry[AutoBotConfig.HANDLER_TYPE] == 'COMMAND':
            hdl = cls._build_command_handler(config, entry, cls._build_idfilter(settings))
        elif entry[AutoBotConfig.HANDLER_TYPE] == 'MESSAGE':
            hdl = cls._build_message_handler(config, entry, cls._build_idfilter(settings))
        elif  entry[AutoBotConfig.HANDLER_TYPE] == 'REGEX':
            hdl = cls._build_regex_handler(config, entry, cls._build_idfilter(settings))
        else:
            cls._logger.error('Not a valid "%s": %s, in %s',
                              AutoBotConfig.HANDLER_TYPE,
                              entry[AutoBotConfig.HANDLER_TYPE],
                              entry[AutoBotConfig.ID])

        return hdl

    @classmethod
    def _build_idfilter(cls, settings):
        return IdFilter(settings[AutoBotSettings.RESTRICT_CHAT_IDS],
                        settings[AutoBotSettings.ACCEPT_CHAT_IDS])

    @classmethod
    def _build_command_handler(cls, config, entry, ids_filter):
        # TODO check_command_attributes(entry)
        cls._logger.debug('Building command handler for entry: %s', entry)
        return CommandHandler(entry[AutoBotConfig.ON],
                              cls._build_response_handler(config, entry),
                              filters=ids_filter)

    @classmethod
    def _build_message_handler(cls, config, entry, ids_filter):
        # TODO check_message_attributes(entry)
        cls._logger.debug('Building message handler for entry: %s', entry)
        # It can't be used anymore. RegexHandler doesn't not support additional filters
        #return RegexHandler(entry['on'], self._default_handler(entry), filters=ids_filter) 
        return MessageHandler(TextEqualsFilter(entry[AutoBotConfig.ON]) & ids_filter,
                              cls._build_response_handler(config, entry))
    
    @classmethod
    def _build_regex_handler(cls, config, entry, ids_filter):
        # TODO check_command_attributes(entry)
        cls._logger.debug('Building regex handler for entry: %s', entry)
        return FilterRegexHandler(ids_filter,
                                  entry[AutoBotConfig.ON],
                                  cls._build_response_handler(config, entry))

    @classmethod
    def _build_response_handler(cls, config, entry):
        response_handler_class = PluginsLoader.get_response_handler_class(entry[AutoBotConfig.RESPONSE_TYPE])
        response_handler = response_handler_class()
        handler = response_handler.setup(config, entry)
        return handler