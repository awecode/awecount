from .base import *
from .cbms_nepal import CBMS_NEPAL
try:
    from .env import *
except ImportError:
    from .test import *