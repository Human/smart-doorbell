import time, threading, ConfigParser, os, logging

class Configurator(threading.Thread):
    """
    Read the configuration file and inform interested classes of relevant values.
    This thread runs parallel to the other top-level thread, Doorbell.
    """

    def __init__(self, config_file):
        """
        Watches config_file and informs ding, dong, and/or openhab_informer of changes
        they should incorporate while running.
        """
        threading.Thread.__init__(self)
        self.daemon = True
        self.running = True
        self.config_file = config_file
        self.timestamp = 0.0 # when the file was last updated
        self.scp = ConfigParser.SafeConfigParser()
        self.ding = None
        self.dong = None
        self.openhab_informer = None
        self.logging = logging.getLogger(self.__class__.__name__)

    def run(self):
        """
        If the timestamp has changed, (re)load config_file and send the latest
        values to the interested parties. It is up to the receiving classes to
        decide if the 'new' value is actually different.
        """
        while self.running:
            new_ts = os.stat(self.config_file).st_mtime
            if new_ts != self.timestamp:
                self.scp.read(self.config_file)
                self.logging.info("(" + self.__class__.__name__ + ") (re)parsed " + self.config_file)
                self.timestamp = new_ts

                if self.ding is not None:
                    self.ding.setsoundfile(self.scp.get('sound', 'ding_soundfile'))
                    self.ding.setlocation(self.scp.get('sound', 'noise_location'))
                if self.dong is not None:
                    self.dong.setsoundfile(self.scp.get('sound', 'dong_soundfile'))
                    self.dong.setlocation(self.scp.get('sound', 'noise_location'))
                    self.dong.setdelay(self.scp.getfloat('sound', 'dong_delay'))
                if self.openhab_informer is not None:
                    self.openhab_informer.seturl(self.scp.get('openhab', 'openhab_doorbell_base_URL'))
                    self.openhab_informer.settimeout(self.scp.getint('openhab', 'timeout'))
            
            time.sleep(1)

    def getint(self, section, option):
        """
        A wrapper to self.scp.getinteger()
        """
        return self.scp.getint(section, option)

    def getboolean(self, section, option):
        """
        A wrapper to self.scp.getboolean()
        """
        return self.scp.getboolean(section, option)

    def register_listeners(self, ding, dong, openhab_informer):
        self.ding = ding
        self.dong = dong
        self.openhab_informer = openhab_informer

    def ready(self):
        return self.timestamp != 0.0

    def stop(self):
        self.running = False
