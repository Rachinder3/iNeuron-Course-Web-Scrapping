import logging


class Logger():
    def __init__(self, filename):
        # logging.basicConfig(filename=filename, format='%(asctime)s %(levelname)s %(message)s', level=logging.INFO)
        self.__logger = logging.getLogger(filename)
        self.__logger.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
        fileHandler = logging.FileHandler(filename)
        fileHandler.setFormatter(formatter)
        self.__logger.addHandler(fileHandler)

    def add_log(self, message, mode='info'):
        if mode == 'debug':
            self.__logger.debug(message)

        if mode == 'info':
            self.__logger.info(message)

        if mode == 'warning':
            self.__logger.warning(message)

        if mode == 'error':
            self.__logger.error(message)

        if mode == 'critical':
            self.__logger.critical(message)
