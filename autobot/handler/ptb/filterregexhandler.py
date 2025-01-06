#!/usr/bin/env python

""" This module contains custom filters used by AutoBot module """

from telegram.ext import StringRegexHandler


class FilterRegexHandler(StringRegexHandler):
    """Expand functionality of RegexHandler allowing user to attach also filters"""

    def __init__(self, filters, *args, **kwargs):
        StringRegexHandler.__init__(self, *args, **kwargs)
        self.filters = filters

    def check_update(self, update):
        if StringRegexHandler.check_update(self, update):
            if not self.filters:
                res = True
            else:
                message = update.effective_message
                if isinstance(self.filters, list):
                    res = any(func(message) for func in self.filters)
                else:
                    res = self.filters(message)
        else:
            res = False
        return res
