import logging
import os
import sys
import subprocess

from autobot.configuration import AutoBotConfig
from autobot.constants import AutoBotConstants
from autobot.handler.response import ResponseHandler

__dynamoclass__ = 'CommandResponseHandler'

class ResponseParseMode(object):
    SEND_EXIT_CODE = 'send_exit_code'
    SEND_STDOUT = 'send_stdout'
    SEND_STDERR = 'send_stderr'
    TIMEOUT = 'timeout'
    ON_SHELL = 'on_shell'

class CommandResponseHandler(ResponseHandler):     

    def _build_response(self, response, response_type_opt, update):
        return _CommandExecutor.execute(response,
                                        response_type_opt,
                                        update)
    
    def _handle_response(self, bot, update, response, response_type_opt):
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
        if isinstance(response_type_opt, dict):
            if ResponseParseMode.SEND_EXIT_CODE in response_type_opt:
                if not isinstance(response_type_opt[ResponseParseMode.SEND_EXIT_CODE], bool):
                    raise TypeError('''"send_exit_code" in "{}" entry,
                    must be a boolean'''.format(entry_id))
            if ResponseParseMode.SEND_STDOUT in response_type_opt:
                if not isinstance(response_type_opt[ResponseParseMode.SEND_STDOUT], bool):
                    raise TypeError('''"send_stdout" in "{}" entry,
                    must be a boolean'''.format(entry_id))
            if ResponseParseMode.SEND_STDERR in response_type_opt:
                if not isinstance(response_type_opt[ResponseParseMode.SEND_STDERR], bool):
                    raise TypeError('''"send_stderr" in "{}" entry,
                    must be a boolean'''.format(entry_id))
            if ResponseParseMode.TIMEOUT in response_type_opt:
                if not isinstance(response_type_opt[ResponseParseMode.TIMEOUT], int):
                    raise TypeError('''"timeout" in "{}" entry,
                    must be a boolean'''.format(entry_id))
        else:
            raise TypeError('''Invalid type for "response_type_options"
            in "{}" entry. It must be a dictionary, 
            see documentation for the correct usage
            of this attribute'''.format(entry_id)) 
    
    @classmethod
    def set_default_options(cls, entry_id, response_type_opt):
        rpm = ResponseParseMode

        defaults = {
            rpm.ON_SHELL : False,
            rpm.SEND_EXIT_CODE : True,
            rpm.SEND_STDOUT : True,
            rpm.SEND_STDERR : True,
            rpm.TIMEOUT : 10
        }

        # No "response_type_options" defined at all, although the "response_type" is set to  "COMMAND"
        if response_type_opt is None:
            response_type_opt = defaults
        
        # Filling the "response_type_options" where undefined
        extra_attributes = response_type_opt

        if rpm.ON_SHELL not in extra_attributes:
            extra_attributes[rpm.ON_SHELL] = defaults[rpm.ON_SHELL]
        if rpm.SEND_EXIT_CODE not in extra_attributes:
            extra_attributes[rpm.SEND_EXIT_CODE] = defaults[rpm.SEND_EXIT_CODE]
        if rpm.SEND_STDOUT not in extra_attributes:
            extra_attributes[rpm.SEND_STDOUT] = defaults[rpm.SEND_STDOUT]
        if rpm.SEND_STDERR not in extra_attributes:
            extra_attributes[rpm.SEND_STDERR] = defaults[rpm.SEND_STDERR]
        if rpm.TIMEOUT not in extra_attributes:
            extra_attributes[rpm.TIMEOUT] = defaults[rpm.TIMEOUT]

        return response_type_opt

class _CommandExecutor(object):

    _logger = logging.getLogger(__name__)

    @classmethod
    def execute(cls, command, options, update):
        """Execute given command. It return always a ready-to-use
        message (one or more) that contains the output of a program according to supplied options"""

        # Replacing {message.*} occurence if needed
        command = command.format(message=update.message)

        cls._logger.debug('Going to execute "%s" with options: %s', command, options)

        timeout = options[ResponseParseMode.TIMEOUT]
        stdout = options[ResponseParseMode.SEND_STDOUT]
        stderr = options[ResponseParseMode.SEND_STDERR]  
        onshell = options[ResponseParseMode.ON_SHELL]  

        stdout = subprocess.PIPE if stdout else None
        stderr = subprocess.PIPE if stderr else None

        # Combine stderr and stdout if necessary
        if stdout == stderr == subprocess.PIPE:
            stderr = subprocess.STDOUT
        
        try:
            completed_proc = subprocess.run(command if onshell else command.split(),\
                                            input=None,\
                                            timeout=timeout,\
                                            check=False,\
                                            stdout=stdout,\
                                            stderr=stderr,\
                                            shell=onshell)
            cls._logger.debug('Execution of "%s" termined with code: %i', command, completed_proc.returncode)
            return cls._build_response(completed_proc, options)
        except subprocess.TimeoutExpired: # TODO aggiungere le altre eccezioni che subprocess.run puo' lanciare (permessi insufficienti)
            cls._logger.error('Timeot expired while executing %s', command)
            return 'Timeout expired, subprocess killed!' # TODO questa non va bene

    @classmethod
    def _build_response(cls, completed_proc, options):
        # TODO multiple message creation if one message exceed MAX_MESSAGE_LENGHT
        exit_code = options[ResponseParseMode.SEND_EXIT_CODE]
        message_str = ''

        if completed_proc.stdout:
            message_str += completed_proc.stdout.decode('utf-8') # TODO utf-8 configurabile
        
        if completed_proc.stderr:
            message_str += completed_proc.stderr.decode('utf-8') # TODO utf-8 configurabile

        if message_str == '':
            message_str = 'Done!'

        if exit_code:
            message_str += '\n**Exit code: {}**'.format(completed_proc.returncode)

        return message_str