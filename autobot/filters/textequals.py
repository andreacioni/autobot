import logging

from telegram.ext.filters import MessageFilter


class TextEqualsFilter(MessageFilter):
    """Custum filter class that allow only one message to be accepted"""

    def __init__(self, text):
        self._text = text
        MessageFilter.__init__(self)

    def filter(self, message):
        return bool(message.text) and (self._text == message.text)
