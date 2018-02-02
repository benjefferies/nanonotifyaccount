import logging

import sys

logging.basicConfig()
root = logging.getLogger()
root.setLevel(logging.INFO)

ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.INFO)
root.addHandler(ch)