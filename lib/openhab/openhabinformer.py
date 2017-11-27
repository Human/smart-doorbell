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
import logging
import threading
import time
from igolibs.haupdater import HAUpdater


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
        self.pressed_at = 0
        self.informed_off = True
        self.logging = logging.getLogger(self.__class__.__name__)
        self.openhab_base_url = None
        self.hass_base_url = None
        self.item_name = None
        self.entity_id = None
        self.haupdater = HAUpdater()
        self.timeout = 0
        self.collapseinterval = 0

    def set_openhab(self, url, item_name):
        """
        POST to this url to update this item's state when the doorbell is pressed or released.
        """
        self.openhab_base_url = url
        self.item_name = item_name

    def set_hass(self, url, entity_id):
        """
        POST to this url to update this entity_id when the doorbell is pressed or released.
        """
        self.hass_base_url = url
        self.entity_id = entity_id

    def settimeout(self, timeout):
        """
        Set the timeout, in seconds, after which we give up on trying to GET a URL.
        """
        self.timeout = timeout

    def setcollapseinterval(self, collapseinterval):
        """
        Set the timeout, in seconds, that must pass after an OFF press before we send
        openHAB an OFF state change. Prevents 'spamming' openHAB with tons of update
        events if someone pounds the doorbell relentlessly.
        """
        self.collapseinterval = collapseinterval

    def run(self):
        """
        POST separate payloads to separate endpoints when the doorbell is pressed and released.
        """
        while self.running:
            try:
                if self.get_on:  # button pressed
                    if time.time() - self.pressed_at > self.collapseinterval:
                        # Enough time has passed since the last ON press; we can send this ON event
                        self.logging.debug("(" + self.__class__.__name__ + ") " + self.openhab_base_url +
                                           " | " + self.item_name)
                        self.haupdater.updateOpenhab(self.openhab_base_url, {self.item_name: 'ON'})
                        self.logging.debug("(" + self.__class__.__name__ + ") " + self.hass_base_url +
                                           " | " + self.entity_id)
                        self.haupdater.updateHASS(self.hass_base_url, self.entity_id, {'state': 'on'})
                        self.logging.info("(" + self.__class__.__name__ + ") doorbell ON")
                        self.informed_off = False
                    self.pressed_at = time.time()  # always remember the last time the button was pressed
                if self.get_off:  # button released
                    if time.time() - self.pressed_at > self.collapseinterval:
                        # Enough time has passed since the last ON press; we can send this OFF event
                        self.logging.debug("(" + self.__class__.__name__ + ") " + self.openhab_base_url +
                                           " | " + self.item_name)
                        self.haupdater.updateOpenhab(self.openhab_base_url, {self.item_name: 'OFF'})
                        self.logging.debug("(" + self.__class__.__name__ + ") " + self.hass_base_url +
                                           " | " + self.entity_id)
                        self.haupdater.updateHASS(self.hass_base_url, self.entity_id, {'state': 'off'})
                        self.logging.info("(" + self.__class__.__name__ + ") doorbell OFF")
                        self.informed_off = True
                        # Start the timing cycle over again; the next press will count as the start of a new cycle.
                        self.pressed_at = 0
                if not self.get_on and not self.get_off and not self.informed_off:
                    if time.time() - self.pressed_at > self.collapseinterval:
                        self.logging.debug("(" + self.__class__.__name__ + ") " + self.openhab_base_url +
                                           " | " + self.item_name)
                        self.haupdater.updateOpenhab(self.openhab_base_url, {self.item_name: 'OFF'})
                        self.logging.debug("(" + self.__class__.__name__ + ") " + self.hass_base_url +
                                           " | " + self.entity_id)
                        self.haupdater.updateHASS(self.hass_base_url, self.entity_id, {'state': 'off'})
                        self.logging.info("(" + self.__class__.__name__ + ") doorbell OFF")
                        self.informed_off = True
                        self.pressed_at = 0
            except Exception as e:
                self.logging.warning("(" + self.__class__.__name__ + ") couldn't inform HA")
                self.logging.warning("(" + self.__class__.__name__ + ") " + str(e))

            self.get_on = False
            self.get_off = False
            time.sleep(0.01)

    def stop(self):
        self.running = False

    def inform(self, on=True):
        """
        Informs home automation whenever the doorbell is pressed or released.
        """
        if on:
            self.get_on = True
            self.get_off = False
        else:
            self.get_on = False
            self.get_off = True

