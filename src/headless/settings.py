# coding=utf-8
"""InaSAFE Headless settings."""

__copyright__ = "Copyright 2018, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'

import os

# Setting for output directory where to store the output layers.
OUTPUT_DIRECTORY = os.environ.get('INASAFE_OUTPUT_DIR')
