import pycommon.dynamo as dynamo

from pycommon.caseinsensitivedict import CaseInsensitiveDict

class PluginsLoader(object):
    
    RESPONSE_HANDLER_PLUGIN_PKG = 'autobot.plugins.response'
    RESPONSE_HANDLER_PLUGIN_SUFFIX = 'ResponseHandler'
    
    _response_handler_classes = CaseInsensitiveDict()

    @classmethod
    def load(cls):
        #Response handler dynamic modules loading and instatiating
        resp_hdl_classes = dynamo.load_classes(PluginsLoader.RESPONSE_HANDLER_PLUGIN_PKG)
        for key, clasz in resp_hdl_classes.items():
            cls._response_handler_classes[key[:-len(cls.RESPONSE_HANDLER_PLUGIN_SUFFIX)]] = clasz

    @classmethod
    def get_all_response_handler_classes(cls):
        return cls._response_handler_classes

    @classmethod
    def has_response_handler(cls, name):
        return name in cls.get_all_response_handler_classes()
    
    @classmethod
    def get_response_handler_class(cls, name):
        return cls._response_handler_classes[name]
