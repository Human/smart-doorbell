import time, threading, urllib2, logging

class OpenHABInformer(threading.Thread):
    """
    Simulates a button press for openHAB via its RESTful HTTP API, so that
    it can perform side effects like notification, logging, recording,
    lighting, etc.
    """

    def __init__(self):
        threading.Thread.__init__(self)
        self.daemon = True
        self.running = True
        self.get_off = False
        self.get_on = False
        self.logging = logging.getLogger(self.__class__.__name__)

    def seturl(self, baseurl):
        """
        Uses the base URL to derive two target URLs: one to GET when the button is
        pressed, one to GET when it is released.
        """
        self.url_on = baseurl+"=ON"
        self.url_off = baseurl+"=OFF"

    def settimeout(self, timeout):
        """
        Set the timeout, in seconds, after which we give up on trying to GET a URL.
        """
        self.timeout = timeout

    def run(self):
        """
        GET baseurl+'ON' when the doorbell is pressed, and baseurl+'OFF' when it is released.
        """
        while self.running:
            try:
                if self.get_on:
                    self.logging.debug(self.url_on)
                    urllib2.urlopen(self.url_on, timeout=self.timeout)
                    self.logging.info("(" + self.__class__.__name__ + ") doorbell ON")
                if self.get_off:
                    self.logging.debug(self.url_off)
                    urllib2.urlopen(self.url_off, timeout=self.timeout)
                    self.logging.info("(" + self.__class__.__name__ + ") doorbell OFF")
            except:
                self.logging.warn("(" + self.__class__.__name__ + ") couldn't inform openHAB")

            self.get_on = False
            self.get_off = False
            time.sleep(0.01)

    def stop(self):
        self.running = False

    def inform(self, on=True):
        """
        Informs openHAB whenever the doorbell is pressed or released.
        """
        if on:
            self.get_on = True
            self.get_off = False
        else:
            self.get_on = False
            self.get_off = True

