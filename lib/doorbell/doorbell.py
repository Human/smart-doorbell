"""
Copyright (C) 2014 Bob Igo, http://bob.igo.name, bob@igo.name

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
import RPi.GPIO as GPIO
import time, threading, logging

class Doorbell(threading.Thread):
    """
    Listen for the doorbell button press and initiate side effects when
    pressed. Side effects include audio playback and  audio and video recording.
    """

    def __init__(self, input_pin, reverse_logic, ding, dong, ha_informer):
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
        self.ha_informer = ha_informer
        self.ha_informer.start()

        if self.reverse_logic:
            self.ding_edge = GPIO.FALLING
            self.dong_edge = GPIO.RISING
        else:
            self.ding_edge = GPIO.RISING
            self.dong_edge = GPIO.FALLING

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.inpin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        self.logging = logging.getLogger(self.__class__.__name__)

    def run(self):
        """
        Start honoring doorbell button presses.
        """
        while self.running:
            GPIO.wait_for_edge(self.inpin, self.ding_edge)
            self.ding.play()
            self.ha_informer.inform(True)

            GPIO.wait_for_edge(self.inpin, self.dong_edge)
            self.dong.play()
            self.ha_informer.inform(False)

    def stop(self):
        """
        Stop honoring doorbell button presses. Stop all support sub-threads.
        """
        self.running = False
        GPIO.cleanup()
        self.ding.stop()
        self.dong.stop()
        self.ha_informer.stop()
