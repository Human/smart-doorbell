import RPi.GPIO as GPIO
import time, threading, logging

class Doorbell(threading.Thread):
    """
    Listen for the doorbell button press and initiate side effects when
    pressed. Side effects include audio playback and  audio and video recording.
    """

    def __init__(self, input_pin, reverse_logic, ding, dong, openhab_informer):
        """
        Create a doorbell that listens on input_pin and plays a 'ding'
        sound when it's pressed and a 'dong' sound when it's released.
        """
        threading.Thread.__init__(self)
        self.daemon = True
        self.running = True
        self.inpin = input_pin
        self.reverse_logic = reverse_logic
        self.ding = ding
        self.dong = dong
        self.ding.start()
        self.dong.start()
        self.openhab_informer = openhab_informer
        self.openhab_informer.start()

        if self.reverse_logic:
            self.ding_edge = GPIO.FALLING
            self.dong_edge = GPIO.RISING
        else:
            self.ding_edge = GPIO.RISING
            self.dong_edge = GPIO.FALLING

        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self.inpin, GPIO.IN)
        self.logging = logging.getLogger(self.__class__.__name__)

    def run(self):
        """
        Start honoring doorbell button presses.
        """
        while self.running:
            GPIO.wait_for_edge(self.inpin, self.ding_edge)
            self.ding.play()
            self.openhab_informer.inform(True)

            GPIO.wait_for_edge(self.inpin, self.dong_edge)
            self.dong.play()
            self.openhab_informer.inform(False)

    def stop(self):
        """
        Stop honoring doorbell button presses. Stop all support sub-threads.
        """
        self.running = False
        GPIO.cleanup()
        self.ding.stop()
        self.dong.stop()
        self.openhab_informer.stop()
