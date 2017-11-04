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
from lib.doorbell.doorbell import Doorbell
from lib.noisemaker.noisemaker import NoiseMaker
from lib.configurator.configurator import Configurator
from lib.openhab.openhabinformer import OpenHABInformer

import time, logging, logging.config

configurator = Configurator('doorbell_config.ini')
logging.config.fileConfig('logging.conf', disable_existing_loggers=False)
logging = logging.getLogger('doorbell_wrapper')

try:
    logging.info('STARTING')
    noise_maker_ding = NoiseMaker(1)
    noise_maker_dong = NoiseMaker(2)
    ha_informer = OpenHABInformer()
    configurator.register_listeners(noise_maker_ding, noise_maker_dong, ha_informer)
    configurator.start()
    while not configurator.ready():
        time.sleep(0.500)
        pass
    
    doorbell = Doorbell(int(configurator.getint('io', 'input_pin')), configurator.getboolean('io', 'reverse_logic'), noise_maker_ding, noise_maker_dong, ha_informer)
    doorbell.start()
    
    logging.info('STARTED')
    
    while True:
        time.sleep(300)

except KeyboardInterrupt:
    doorbell.stop()
    configurator.stop()
