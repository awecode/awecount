from .base import *  # noqa
from .cbms_nepal import *  # noqa

try:
    from .env import *  # type: ignore # noqa
except ImportError:
    from .prod import *  # noqa
