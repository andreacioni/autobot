#!/usr/bin/env python

""" AutoBot module """

import logging

from sys import version_info as pyversion

from telegram.ext import Updater, ConversationHandler

from .configuration import AutoBotConfig, AutoBotSettings
from .factory import CallbackHandlerFactory
from .plugins import PluginsLoader

# Loading dynamic plugin modules before starting
PluginsLoader.load()

class AutoBot(object):

    """ This is the main class of AutoBot, almost all work is done here """

    def __init__(self, settings_file, configuration_dir):
        self._logger = logging.getLogger(__name__)
        self._settings = AutoBotSettings(settings_file).load()
        self._config = AutoBotConfig(self._settings, configuration_dir).load()

    def _error(self, bot, update, error):
        pass

    def _parse_config(self):
        """ Transforming entries in appropriate handler """
        entries = self._config.get()

        self._logger.info('Parsing entries content')
        handlers = {}
        entry_points = []
        fallbacks = []

        for entry in entries:
            # Build an appropriate handler based on given configuration
            hdl = CallbackHandlerFactory.build_callback(self._settings, self._config, entry)

            # Add built handler to the appropriate group (state). Remember that every entry
            # could belong to multiple groups
            for group in entry[AutoBotConfig.GROUP]:
                if entry[AutoBotConfig.ENTRY_POINT]:
                    entry_points.append(hdl)
                elif entry[AutoBotConfig.IS_FALLBACK]:
                    fallbacks.append(hdl)
                else:
                    if not group in handlers:
                        handlers[group] = [hdl]
                    else:
                        handlers[group].append(hdl)

        return entry_points, fallbacks, handlers

    def _register_handlers(self, dispatcher):

        self._logger.info('Registering handlers')

        entry_points, fallbacks_list, handlers_dict = self._parse_config()

        reentry = self._settings[AutoBotSettings.ALLOW_REENTRY]

        # Printing some debug informations
        self._logger.debug("Groups: %s", handlers_dict)
        self._logger.debug("Entry points: %s", entry_points)
        self._logger.debug("Fallback: %s", fallbacks_list)

        # At least one entry point has to be defined in configuration
        if not entry_points:
            raise RuntimeError("At least one entry point has to be defined in configuration")

        dispatcher.add_handler(ConversationHandler(
            entry_points,
            handlers_dict,
            fallbacks_list,
            allow_reentry=reentry
        ))


    def startup(self):
        """ Starting point of AutoBot program"""

        self._logger.info('Starting AutoBot - v.0.0.1 (on Python %i.%i.%i)', pyversion.major, pyversion.minor, pyversion.micro)

        if(pyversion.major < 3):
            self._logger.warn('Detected Python version 2.x, consider to switch to newer version')

        # Create the EventHandler and pass it your bot's token.
        self._logger.info('Creating updater...')
        updater = Updater(self._settings[AutoBotSettings.API_KEY],\
                          workers=self._settings[AutoBotSettings.WORKERS])

        # Get the dispatcher to register handlers
        dispatcher = updater.dispatcher

        # Register handlers to the dispatcher object
        self._register_handlers(dispatcher)

        self._logger.info('Everything done! Starting polling phase...')

        # Start the Bot
        updater.start_polling()

        # Run the bot until you press Ctrl-C or the process receives SIGINT,
        # SIGTERM or SIGABRT. This should be used most of the time, since
        # start_polling() is non-blocking and will stop the bot gracefully.
        updater.idle()
