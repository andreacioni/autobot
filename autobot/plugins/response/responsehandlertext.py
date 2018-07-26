import logging

from autobot.constants import AutoBotConstants
from autobot.configuration import AutoBotConfig
from autobot.handler.response import ResponseHandler

__dynamoclass__ = 'TextResponseHandler'

class TextResponseHandler(ResponseHandler):
    
    def _build_response(self, response, response_type_opt, udpate):
        return response

    def _handle_response(self, bot, update, response, response_type_opt):
        self._logger.debug('Built keyboard is: %s', self._keyboard_markup)
        if self._keyboard_markup:
            bot.send_message(update.message.chat_id, \
                            response, \
                            parse_mode=AutoBotConstants.PARSE_DICT[self._entry[AutoBotConfig.RESPONSE_PARSE_MODE]],\
                            reply_markup=self._keyboard_markup)
        else:
            bot.send_message(update.message.chat_id, \
                                response, \
                                parse_mode=AutoBotConstants.PARSE_DICT[self._entry[AutoBotConfig.RESPONSE_PARSE_MODE]])

    @classmethod
    def check_options(cls, entry_id, response_type_opt):
        if response_type_opt is not None:
           logging.getLogger(__name__).warning('Response type options defined while response type is "TEXT"')
    
    @classmethod
    def set_default_options(self, entry_id, response_type_opt):
        if response_type_opt is not None:
           logging.getLogger(__name__).warning('Response type options defined while response type is "TEXT"')

        return response_type_opt