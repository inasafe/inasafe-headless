# coding=utf-8
from celery import Celery

__copyright__ = "Copyright 2018, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'

app = Celery('headless.tasks')
app.config_from_object('headless.celeryconfig')

packages = (
    'headless',
)


# initialize qgis_app
from safe.test.utilities import get_qgis_app  # noqa
QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()


app.autodiscover_tasks(packages)

if __name__ == '__main__':
    app.worker_main()
