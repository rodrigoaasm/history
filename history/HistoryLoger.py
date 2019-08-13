import logging
from logging import config as config_log
from colorlog import ColoredFormatter

class HistoryLog:
    def __init__(self, log_level = config.log_level, 
        LOG_FORMAT = "[%(log_color)s%(asctime)-8s%(reset)s] |%(log_color)s%(module)-8s%(reset)s| %(log_color)s%(levelname)s%(reset)s: %(log_color)s%(message)s%(reset)s", isDisabled = False):

        #Disable all others modules logs
        LOGGING = {
            'version': 1,
            'disable_existing_loggers': True,
        }
        
        dateFormat = '%d/%m/%y - %H:%M:%S'
        config_log.dictConfig(LOGGING)
        self.formatter = ColoredFormatter(LOG_FORMAT, dateFormat)
        self.log = logging.getLogger('history.' + __name__)
        self.log.setLevel(log_level)
        self.log.disabled = isDisabled
        self.level = log_level

        if not getattr(self.log, 'handler_set', None):
            self.stream = logging.StreamHandler()
            self.stream.setLevel(log_level)
            self.stream.setFormatter(self.formatter)
            self.log.setLevel(log_level)
            self.log.addHandler(self.stream)
            self.log.handler_set = True

    def update_log_level(self, LEVEL):
        levelToName = ['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'NOTSET']

        try:
            self.log = logging.getLogger('history.' + __name__)
            for hdlr in self.log.handlers[:]:
                self.log.removeHandler(hdlr)

            self.stream = logging.StreamHandler()
            self.stream.setLevel(LEVEL)
            self.stream.setFormatter(self.formatter)

            self.log.setLevel(LEVEL)
            self.log.addHandler(self.stream)
            self.log.handler_set = True

            self.level = LEVEL

        except ValueError:
            raise HTTPRequestError(400, "Unknown level: {} valid are {}".format(LEVEL, levelToName))
    
    def get_log_level(self):
        return self.level

    def color_log(self):
        return self.log
