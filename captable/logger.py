# Logging helpers
from __future__ import absolute_import

import logging

# Logging throughout this package uses this logger -- change as appropriate to
# match logging preferences
logging.basicConfig(level=logging.WARN)
logger = logging.getLogger("")
