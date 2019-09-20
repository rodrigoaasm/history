#logging
import logging
import falcon
from logging import config as config_log
from colorlog import ColoredFormatter

class Log:
    
    levelToName = dict([(50,'CRITICAL'), (40,'ERROR'), (30,'WARNING'), (20,'INFO'), (10,'DEBUG')])
    
    def __init__(self, log_level=logging.DEBUG,
                 log_format="[%(log_color)s%(asctime)-8s%(reset)s] |%(log_color)s%(module)-8s%(reset)s| %(log_color)s%(levelname)s%(reset)s: %(log_color)s%(message)s%(reset)s", is_disabled=False):
             
        #Disable all others modules logs
        log_config = {
            'version': 1,
            'disable_existing_loggers': True,
        }

        date_format = '%d/%m/%y - %H:%M:%S'
        config_log.dictConfig(log_config)
        self.formatter = ColoredFormatter(log_format, date_format)
        self.log = logging.getLogger('history.' + __name__)
        self.log.setLevel(log_level)
        self.log.disabled = is_disabled

        if not getattr(self.log, 'handler_set', None):
            self.stream = logging.StreamHandler()
            self.stream.setLevel(log_level)
            self.stream.setFormatter(self.formatter)
            self.log.setLevel(log_level)
            self.log.addHandler(self.stream)
            self.log.handler_set = True
    
    @staticmethod
    def update_log_level(logger, level):
        logger.setLevel(level.upper())

    def color_log(self):
        """
        Returns a logger
        """
        return self.log
