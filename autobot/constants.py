from telegram.constants import ParseMode


class AutoBotConstants(object):
    """This class holds all the constants used by AutoBot"""

    HANDLER_TYPES = ("COMMAND", "MESSAGE", "REGEX")
    PARSE_DICT = {"NONE": None, "HTML": ParseMode.HTML, "MARKDOWN": ParseMode.MARKDOWN}
    MAX_MESSAGE_LENGTH = 4096
