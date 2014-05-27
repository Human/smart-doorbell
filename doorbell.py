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
    openhab_informer = OpenHABInformer()
    configurator.register_listeners(noise_maker_ding, noise_maker_dong, openhab_informer)
    configurator.start()
    while not configurator.ready():
        time.sleep(0.500)
        pass
    
    doorbell = Doorbell(int(configurator.getint('io', 'input_pin')), configurator.getboolean('io', 'reverse_logic'), noise_maker_ding, noise_maker_dong, openhab_informer)
    doorbell.start()
    
    logging.info('STARTED')
    
    while True:
        time.sleep(300)

except KeyboardInterrupt:
    doorbell.stop()
    configurator.stop()
