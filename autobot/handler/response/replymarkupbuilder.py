import logging

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton

from autobot import AutoBotConstants
from autobot.configuration import AutoBotConfig

class ReplyMarkupBuilder(object):
    
    _logger = logging.getLogger(__name__)

    @classmethod
    def build_keyboard(cls, config, entry):
        """Build the keyboard according to the entry's specs.
        This method returns:
            - None: keyboard need to be left on the screen (if already displayed)
            - Instance of ReplyKeyboardMarkup that holds the new keyboard to be displayed
            - Instance of ReplyKeyboardRemove means that a currently displayed keyboard need to be remove"""
        
        button_list = cls._build_keyboard_markup(config, entry)

        if button_list is not None:
            if button_list: # If button_list is a not empty array we proceed to build the keyboard
                keyboard_markup = ReplyKeyboardMarkup(\
                                button_list, \
                                entry[AutoBotConfig.RESIZE_KEYBOARD]\
                                    if AutoBotConfig.RESIZE_KEYBOARD in entry else False, \
                                entry[AutoBotConfig.ONE_TIME_KEYBOARD]\
                                    if AutoBotConfig.ONE_TIME_KEYBOARD in entry else False)
            else:
                keyboard_markup = None # Leave the previous keyboard. This is the default behaviour
        else:
            keyboard_markup = ReplyKeyboardRemove() # Remove the keyboard if KEYBOARD_OPTIONS = None (null)

        return keyboard_markup

    @classmethod
    def _build_keyboard_markup(cls, config, entry):
        """This method returns:
            - None: remove previous defined keyboard, if exists
            - []: leaving the previous defined keyboard, if exists
            - [[...],...]: new keyboard"""
        
        reply_keyboard = []

        # Checking type of KEYBOARD_OPTIONS parameter
        if entry[AutoBotConfig.KEYBOARD_OPTIONS] is None:
            reply_keyboard = None
        elif isinstance(entry[AutoBotConfig.KEYBOARD_OPTIONS], list) or \
             isinstance(entry[AutoBotConfig.KEYBOARD_OPTIONS], str):

            # If "keyboard_options" field is a string we search by "id"
            # for a keyboard previously defined in another entry
            if not isinstance(entry[AutoBotConfig.KEYBOARD_OPTIONS], list):
                ref_id = entry[AutoBotConfig.KEYBOARD_OPTIONS]
                entry[AutoBotConfig.KEYBOARD_OPTIONS] = config[ref_id][AutoBotConfig.KEYBOARD_OPTIONS]

            # If KEYBOARD_OPTIONS is a not empty list we proceed to keyboard button building,
            # otherwise we return an empty array (that, in this context, means leaving a previously
            # defined keyboard)
            if entry[AutoBotConfig.KEYBOARD_OPTIONS]:
                # Then we create the appropriate KeyboardButton istance.
                # Now we add the '/' to every command found in keyboard
                for row in entry[AutoBotConfig.KEYBOARD_OPTIONS]:
                    button_list = []
                    for response_id in row:
                        if config[response_id][AutoBotConfig.HANDLER_TYPE] == 'COMMAND':
                            button_list.append(KeyboardButton('/' + config[response_id][AutoBotConfig.ON]))
                        else:
                            button_list.append(KeyboardButton(config[response_id][AutoBotConfig.ON]))
                    reply_keyboard.append(button_list)
        else:
            cls._logger.warning('Invalid KEYBOARD_OPTIONS parameter in entry: %s. Removing previously defined keyboard', entry[AutoBotConfig.ID])


        return reply_keyboard