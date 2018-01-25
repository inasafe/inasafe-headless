# coding=utf-8
import os
from celery import Celery

# Setting
from safe.utilities.settings import set_setting
from headless.settings import OUTPUT_DIRECTORY

__copyright__ = "Copyright 2018, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'

app = Celery('headless.tasks')
app.config_from_object('headless.celeryconfig')

packages = (
    'headless',
)

# Initialize qgis_app
from safe.test.utilities import get_qgis_app  # noqa
QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()

if OUTPUT_DIRECTORY:
    if not os.path.exists(OUTPUT_DIRECTORY):
        os.makedirs(OUTPUT_DIRECTORY)
    set_setting('defaultUserDirectory', OUTPUT_DIRECTORY)

app.autodiscover_tasks(packages)

if __name__ == '__main__':
    app.worker_main()
