import json

class AutoBotSettings(object):

    API_KEY = 'api_key'
    UNBOUN_MSG = 'unbound_msg'
    WORKERS = 'workers'
    RESTRICT_CHAT_IDS = 'restrict_chat_ids'
    ACCEPT_CHAT_IDS = 'accept_chat_ids'
    ALLOW_REENTRY = 'allow_reentry'

    def __init__(self, settings_file):
        self._settings_file = settings_file
        self._settings = None

    def load(self):
        with open(self._settings_file, encoding='utf-8') as config_f:
            self._settings = json.load(config_f)
        return self
    
    def get(self, key):
        return self._settings[key]

    def __getitem__(self, keys):
        return self.get(keys)
    