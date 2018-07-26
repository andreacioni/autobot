import logging

from telegram.ext import ConversationHandler

from autobot import AutoBotConstants
from autobot.configuration import AutoBotConfig
from autobot.plugins import PluginsLoader

from .replymarkupbuilder import ReplyMarkupBuilder

class ResponseHandler(object):

    def setup(self, config, entry):
        self._logger = logging.getLogger(__name__)
        self._config = config
        self._entry = entry

        self._keyboard_markup = ReplyMarkupBuilder.build_keyboard(config, entry)

        self._logger.debug('Built keyboard is: %s', self._keyboard_markup)

        def handler(bot, update):
            self._log_msg(update.message)

            response = self._build_response(entry[AutoBotConfig.RESPONSE],
                                  entry[AutoBotConfig.RESPONSE_TYPE_OPTIONS],
                                  update)

            self._logger.debug('Built response is: %s', response)

            if not response:
                self._logger.warning("Empty response built. No answer will be sent")
            else:
                self._handle_response(bot, update, response, entry[AutoBotConfig.RESPONSE_TYPE_OPTIONS])
            
            return self._get_to_group(entry)

        return handler

    def _handle_response(self, bot, update, response, response_type_opt):
        raise NotImplementedError

    def _build_response(self, response, response_type_opt, udpate):
        raise NotImplementedError

    @classmethod
    def check_options(cls, entry_id, response_type_opt):
        raise NotImplementedError
    
    @classmethod
    def set_default_options(cls, entry_id, response_type_opt):
        raise NotImplementedError

    def _log_msg(self, message):
        """ Log incoming message """
        self._logger.debug('%s message received from user: %s. ChatID: %s', \
                            message.text, \
                            message.from_user.name, \
                            message.chat.id)

    def _get_to_group(self ,entry):
        ret = None
        if entry[AutoBotConfig.EXIT_POINT]:
            ret = ConversationHandler.END
        else:
            if entry[AutoBotConfig.TO_GROUP]:
                ret = entry[AutoBotConfig.TO_GROUP]
            #else, if TO_GROUP is "None" the destination group doesn't change
        
        self._logger.debug("To group: %s", ret)
        
        return ret