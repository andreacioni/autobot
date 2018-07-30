import logging
import tempfile
import uuid
import base64

from os import remove
from os import path

from urllib.request import urlopen, Request, URLError

from autobot.constants import AutoBotConstants
from autobot.configuration import AutoBotConfig
from autobot.handler.response import ResponseHandler

__dynamoclass__ = 'PhotoResponseHandler'

class ResponseOptional(object):
    CAPTION = 'caption'
    AUTH = "auth"

class AuthOptional(object):
    TYPE = 'type'
    USERNAME = 'username'
    PASSWORD = 'password'

class PhotoResponseHandler(ResponseHandler):
    
    def _build_response(self, response, response_type_opt, udpate):
        try:
            resp = urlopen(self._get_request(response, response_type_opt))
            if resp.getcode() == 200:
                filepath = path.join(tempfile.mkdtemp(), uuid.uuid4().hex)

            with open(filepath, 'wb') as f:
                f.write(resp.read())

            return filepath
        except URLError as e:
            self._logger.error(e)
            return e
       

    def _handle_response(self, bot, update, response, response_type_opt):
        if isinstance(response, URLError):
            bot.send_message(update.message.chat_id, str(response))
        else:
            with open(response, 'rb') as photo_file:
                if self._keyboard_markup:
                    bot.send_photo(update.message.chat_id, \
                                    photo_file, \
                                    caption=response_type_opt[ResponseOptional.CAPTION], \
                                    reply_markup=self._keyboard_markup)
                else:
                    bot.send_photo(update.message.chat_id, \
                                        photo_file, \
                                        caption=response_type_opt[ResponseOptional.CAPTION])

            try:
                remove(photo_file)
            except OSError as e:
                self._logger.error(e)
    
    def _get_request(self, response, response_type_opt):
        if ResponseOptional.AUTH in response_type_opt \
            and AuthOptional.TYPE in response_type_opt[ResponseOptional.AUTH] \
            and AuthOptional.USERNAME in response_type_opt[ResponseOptional.AUTH] \
            and AuthOptional.PASSWORD in response_type_opt[ResponseOptional.AUTH]:
            
            auth = response_type_opt[ResponseOptional.AUTH]
            
            if auth[AuthOptional.TYPE].upper() == 'BASIC':
                return self._get_basic_auth_request(response, auth[AuthOptional.USERNAME], auth[AuthOptional.PASSWORD])
        
        return response

    def _get_basic_auth_request(self, url, username, password):
        request = Request(url)
        base64string = base64.b64encode('{}:{}'.format(username, password).encode())
        request.add_header("Authorization", b'Basic ' + base64string)    
        return request

    @classmethod
    def check_options(cls, entry_id, response_type_opt):
        if response_type_opt is not None \
            and ResponseOptional.CAPTION in response_type_opt \
            and isinstance(response_type_opt[ResponseOptional.CAPTION], str) \
            and len(response_type_opt[ResponseOptional.CAPTION]) > 200:
            raise TypeError('Caption length in "PHOTO" must be less than 200 characters')
    
    @classmethod
    def set_default_options(self, entry_id, response_type_opt):
        if response_type_opt is None:
            response_type_opt = dict()
            
        if ResponseOptional.CAPTION not in response_type_opt:
            response_type_opt[ResponseOptional.CAPTION] = ''

        return response_type_opt