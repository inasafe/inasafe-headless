# coding=utf-8
"""InaSAFE Headless settings."""

__copyright__ = "Copyright 2018, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'

import os
import ast

# Setting for output directory where to store the output layers.
OUTPUT_DIRECTORY = os.environ.get('INASAFE_OUTPUT_DIR')

# GeoNode Settings to push to GeoNode
PUSH_TO_REALTIME_GEONODE = ast.literal_eval(
    os.environ.get('PUSH_TO_REALTIME_GEONODE', 'False'))
REALTIME_GEONODE_USER = os.environ.get('REALTIME_GEONODE_USER')
REALTIME_GEONODE_PASSWORD = os.environ.get('REALTIME_GEONODE_PASSWORD')
REALTIME_GEONODE_URL = os.environ.get('REALTIME_GEONODE_URL')
