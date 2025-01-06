#!/usr/bin/env python

""" This module contains custom filters used by AutoBot module """

from telegram import Update
from telegram.ext import StringRegexHandler


class FilterRegexHandler(StringRegexHandler):
    """Expand functionality of RegexHandler allowing user to attach also filters"""

    def __init__(self, filters, *args, **kwargs):
        StringRegexHandler.__init__(self, *args, **kwargs)
        self.filters = filters

    def check_update(self, update: Update):
        if StringRegexHandler.check_update(self, update.message.text):
            if not self.filters:
                res = True
            else:
                if isinstance(self.filters, list):
                    res = any(filter.check_update(update) for filter in self.filters)
                else:
                    res = self.filters.check_update(update)
        else:
            res = False
        return res
