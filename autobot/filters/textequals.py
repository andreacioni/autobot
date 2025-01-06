import logging

from telegram.ext.filters import BaseFilter


class TextEqualsFilter(BaseFilter):
    """Custum filter class that allow only one message to be accepted"""

    def __init__(self, text):
        self._text = text
        BaseFilter.__init__(self)

    def filter(self, message):
        return bool(message.text) and (self._text == message.text)
