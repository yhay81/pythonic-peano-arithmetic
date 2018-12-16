from logging import getLogger, INFO
import logging.config
import os
pwd = os.path.dirname(os.path.abspath(__file__))
logging.config.fileConfig(os.path.join(pwd, 'logging.conf'))

n_logger = getLogger('nLogger')
z_logger = getLogger('zLogger')
q_logger = getLogger('qLogger')
