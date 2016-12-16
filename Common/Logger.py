class Logger(object):
    DEBUG_LEVEL = 0
    INFO_LEVEL = 1
    ERROR_LEVEL = 2
    ALARM_LEVEL = 3

    @classmethod
    def debug(cls, *args):
        cls._log(cls.DEBUG_LEVEL, *args)

    @classmethod
    def info(cls, *args):
        cls._log(cls.INFO_LEVEL, *args)

    @classmethod
    def error(cls, *args):
        cls._log(cls.ERROR_LEVELL, *args)

    @classmethod
    def alarm(cls, *args):
        cls._log(cls.ALARM_LEVEL, *args)

    @classmethod
    def _log(cls, level, *args):
        pass
