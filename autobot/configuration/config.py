import os
import json
import glob
import logging

from autobot.plugins import PluginsLoader
from autobot.constants import AutoBotConstants
from telegram.constants import MAX_MESSAGE_LENGTH

class AutoBotConfig(object):

    ID = 'id'
    ON = 'on'
    HANDLER_TYPE = 'handler_type'
    RESPONSE_TYPE = 'response_type'
    RESPONSE = 'response'
    RESPONSE_PARSE_MODE = 'response_parse_mode'
    RESPONSE_TYPE_OPTIONS = 'response_type_options'
    KEYBOARD_OPTIONS = 'keyboard_options'
    ONE_TIME_KEYBOARD = 'one_time_keyboard'
    RESIZE_KEYBOARD = 'resize_keyboard'
    IS_FALLBACK = 'is_fallback'
    ENTRY_POINT ='entry_point'
    EXIT_POINT ='exit_point'
    DISABLE_WEB_PAGE_PREVIEW = 'disable_web_page_preview'
    GROUP = 'group'
    TO_GROUP = 'to_group'

    def __init__(self, settings, configuration_dir):
        self._logger = logging.getLogger(__name__)
        self._settings = settings
        self._configuration_dir = configuration_dir
        self._config = None
        self._entries = None

    def load(self):
        """Load configuration files, recursively, from given configuration_dir directory."""
  
        # Load configuration from *.json file inside "config/" directory
        # and store the inside an array
        self._entries = self._load_entries()

        # Check required field inside every entry
        self._check_base_attribute(self._entries)

        # Set default values for undefined field in every entry
        self._set_default_values(self._entries)

        # Array to dictionary conversion made after checks. 
        # This conversion is useful because reduces the search time at runtime.
        # We need second loop to remove AutoBotConfig.ID keys from every values because it is redundant
        self._config = {entry[AutoBotConfig.ID] : entry for entry in self._entries}
        for value in self._config.values():
            del dict(value)[AutoBotConfig.ID] # Deleting AutoBotConfig.ID field from a new copy of 'value' dictionary

        return self

    def get(self):
        """Get loaded configuration as list"""
        return self._entries

    def __getitem__(self, keys):
        return self._config[keys]

    def _check_base_attribute(self, entries):
        """ Check for base attribute and id duplication inside entries """

        self._logger.info('Checking entries attributes')
        
        # Checking if AutoBotConfig.ID, AutoBotConfig.HANDLER_TYPE, AutoBotConfig.ON and AutoBotConfig.RESPONSE field is present inside the entry
        for entry in entries:
            # First check very important parameters
            if AutoBotConfig.ID not in entry:
                raise AttributeError('No \'id\' attribute found inside an entry')
            elif AutoBotConfig.HANDLER_TYPE not in entry:
                raise AttributeError('No \'handler_type\' attribute found inside entry {}'.format(entry[AutoBotConfig.ID]))
            elif AutoBotConfig.ON not in entry:
                raise AttributeError('No \'on\' attribute found inside entry {}'.format(entry[AutoBotConfig.ID]))
            elif (AutoBotConfig.RESPONSE not in entry) or (entry[AutoBotConfig.RESPONSE].strip() == ''):
                raise AttributeError('No \'response\' attribute found inside entry {}, or it is empty'.format(entry[AutoBotConfig.ID]))
            
            # Check validity of HANDLER_TYPE field 
            if entry[AutoBotConfig.HANDLER_TYPE] not in AutoBotConstants.HANDLER_TYPES:
                raise TypeError('"{}" as handler_type is not valid. Allowed {}' \
                                    .format(entry[AutoBotConfig.HANDLER_TYPE], AutoBotConstants.HANDLER_TYPES))         
            
            if (AutoBotConfig.RESPONSE_PARSE_MODE in entry) and (entry[AutoBotConfig.RESPONSE_PARSE_MODE] not in AutoBotConstants.PARSE_DICT):
                raise TypeError('"{}" as response_parse_mode is not valid. Allowed {}' \
                                    .format(entry[AutoBotConfig.RESPONSE_PARSE_MODE], AutoBotConstants.PARSE_DICT))
            # If GROUP is defined it must be a list. At least it can contains only one item
            if (AutoBotConfig.GROUP in entry) and not (isinstance(entry[AutoBotConfig.GROUP], list)):
                raise TypeError('"group" must be a list')
            # If an entry is marked as EXIT_POINT we check if TO_GROUP is defined, in that case we raise an exception
            if (AutoBotConfig.EXIT_POINT in entry) and (AutoBotConfig.TO_GROUP in entry) and entry[AutoBotConfig.EXIT_POINT]:
                raise AttributeError('"{}" is ignored when "{}" is set to "true", in entry "{}"'.format(AutoBotConfig.TO_GROUP, AutoBotConfig.EXIT_POINT, entry[AutoBotConfig.ID])) 

            # We check also for RESPONSE_TYPE_OPTION to be valid. This task is done
            # by the appropriate response handler
            self._check_command_extra_attributes(entry)
        
        # Checking if all ids are different
        ids_list = [entry[AutoBotConfig.ID] for entry in entries]
        for entry_id in ids_list:
            if ids_list.count(entry_id) != 1:
                raise AttributeError('No unique "{}" id found'.format(entry_id))

        # Check that no one AutoBotConfig.ON attribute start with '/'
        on_backslash = [entry[AutoBotConfig.ON] for entry in entries if entry[AutoBotConfig.ON].startswith('/')]
        if on_backslash:
            raise AttributeError('Found at least one \'on\' contains \'/\'.' \
                                    'This is not allowed. on: {}'.format(on_backslash))

        # Check reply text lenght < 4096
        # TODO si puo' ignorare questo controllo, pero' si devono mandare
        # TODO da togliere i controlli per "invalid_option_message" che non e' piu' usato
        # piu' messaggi per coprire la lunghezza complessiva
        text_lenght = [entry[AutoBotConfig.ID] \
                    for entry in entries \
                        if (len(entry[AutoBotConfig.ON]) > MAX_MESSAGE_LENGTH) \
                            or (('invalid_option_message' in entry) and \
                                    (len(entry['invalid_option_message']) > MAX_MESSAGE_LENGTH))]
        if text_lenght:
            raise AttributeError('Found text message lenght > ' + \
                                    str(MAX_MESSAGE_LENGTH) + ' inside: "' + str(text_lenght) + '"')

        #TODO controllare che il gruppo di destinazione possieda le opzioni della tastiera
        
    def _check_command_extra_attributes(self, entry):
        if AutoBotConfig.RESPONSE_TYPE in entry and AutoBotConfig.RESPONSE_TYPE_OPTIONS in entry:
            response_type = entry[AutoBotConfig.RESPONSE_TYPE]
            if PluginsLoader.has_response_handler(response_type):
                response_handler_class = PluginsLoader.get_response_handler_class(response_type)
                response_handler_class.check_options(entry[AutoBotConfig.ID], entry[AutoBotConfig.RESPONSE_TYPE_OPTIONS])
            else:
                raise KeyError('Not a valid response type ({}) defined in entry: {}'.format(response_type, entry[AutoBotConfig.ID]))

    def _set_default_values(self, entries):
        """ Setting default value for undefined field inside every entry """

        self._logger.info('Setting default values for undefined fields')

        for entry in entries:
            if AutoBotConfig.RESPONSE_TYPE_OPTIONS not in entry:
                entry[AutoBotConfig.RESPONSE_TYPE_OPTIONS] = None
            if AutoBotConfig.KEYBOARD_OPTIONS not in entry:
                entry[AutoBotConfig.KEYBOARD_OPTIONS] = []
            if AutoBotConfig.ONE_TIME_KEYBOARD not in entry:
                entry[AutoBotConfig.ONE_TIME_KEYBOARD] = False
            if AutoBotConfig.RESIZE_KEYBOARD not in entry:
                entry[AutoBotConfig.RESIZE_KEYBOARD] = False
            if AutoBotConfig.DISABLE_WEB_PAGE_PREVIEW not in entry:
                entry[AutoBotConfig.DISABLE_WEB_PAGE_PREVIEW] = False
            if AutoBotConfig.RESPONSE_TYPE not in entry:
                entry[AutoBotConfig.RESPONSE_TYPE] = 'TEXT'
            if AutoBotConfig.RESPONSE_PARSE_MODE not in entry:
                entry[AutoBotConfig.RESPONSE_PARSE_MODE] = "NONE"
            if AutoBotConfig.ENTRY_POINT not in entry:
                entry[AutoBotConfig.ENTRY_POINT] = False
            if AutoBotConfig.GROUP not in entry:
                entry[AutoBotConfig.GROUP] = ['__DEFAULT__']
            if AutoBotConfig.TO_GROUP not in entry:
                entry[AutoBotConfig.TO_GROUP] = None
            if AutoBotConfig.EXIT_POINT not in entry:
                entry[AutoBotConfig.EXIT_POINT] = False
            if AutoBotConfig.IS_FALLBACK not in entry:
                entry[AutoBotConfig.IS_FALLBACK] = False
            
            # This ensure that all entry points will have an appropriate "TO_GROUP" setted
            # correctly. If an entry point belong to multiple groups and it haven't a valid
            # "TO_GROUP" setted at this point this code raise an exception.
            # If entry point belongs to only one group we can simply use that as "TO_GROUP"
            if entry[AutoBotConfig.ENTRY_POINT] and not entry[AutoBotConfig.TO_GROUP]:
                if len(entry[AutoBotConfig.GROUP]) ==  1:
                    entry[AutoBotConfig.TO_GROUP] = entry[AutoBotConfig.GROUP][0]
                else:
                    raise RuntimeError('Found "{}" starting point belong to multiple groups and no "TO_GROUP" defined'.format(entry[AutoBotConfig.ID]))

            self._set_defaults_for_command_extra_attributes(entry)

    @classmethod
    def _set_defaults_for_command_extra_attributes(cls, entry):
        if AutoBotConfig.RESPONSE_TYPE in entry and AutoBotConfig.RESPONSE_TYPE_OPTIONS in entry:
            response_type = entry[AutoBotConfig.RESPONSE_TYPE]
            if PluginsLoader.has_response_handler(response_type):
                response_handler_class = PluginsLoader.get_response_handler_class(response_type)
                entry[AutoBotConfig.RESPONSE_TYPE_OPTIONS] = response_handler_class.set_default_options(entry[AutoBotConfig.ID], entry[AutoBotConfig.RESPONSE_TYPE_OPTIONS])
            else:
                raise KeyError('Not a valid response type ({}) defined in entry: {}'.format(response_type, entry[AutoBotConfig.ID]))

    def _load_entries(self):
        """ Loading json configuration files from current directory and subdirectory """

        self._logger.info('Loading json configuration files from current directory')
        ret_array = []
        files = glob.glob(self._configuration_dir + os.sep + '*.json') # TODO case insensitive extension needed

        if not files:
            raise IOError('No files found inside: {}'.format(self._configuration_dir))

        self._logger.debug('Found %i file/s %s', len(files), files)
        for file_path in files:
            self._logger.info('Opening %s file', file_path)
            with open(file_path, encoding='utf-8') as json_fp:
                json_obj = json.load(json_fp)
                if not json_obj or not isinstance(json_obj, list):
                    raise TypeError('Not valid JSON array found in {} file'.format(file_path))
                else:
                    self._logger.info('Found %i item/s in %s file', len(json_obj), file_path)
                    ret_array.extend(json_obj)
        
        return ret_array
