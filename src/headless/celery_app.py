# coding=utf-8
import os

from celery import Celery

from headless.settings import OUTPUT_DIRECTORY
# Setting
from safe.utilities.settings import set_setting

__copyright__ = "Copyright 2018, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'

app = Celery('headless.tasks')
app.config_from_object('headless.celeryconfig')

packages = (
    'headless',
)

# # Initialize qgis_app
# from safe.test.qgis_app import qgis_app  # noqa
# APP, IFACE = qgis_app()
from safe.test.utilities import get_qgis_app
QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()

# Load QGIS Expression
from safe.utilities.expressions import qgis_expressions  # noqa

if OUTPUT_DIRECTORY:
    try:
        os.makedirs(OUTPUT_DIRECTORY)
    except OSError:
        if not os.path.isdir(OUTPUT_DIRECTORY):
            raise
    set_setting('defaultUserDirectory', OUTPUT_DIRECTORY)

app.autodiscover_tasks(packages)

if __name__ == '__main__':
    app.worker_main()
