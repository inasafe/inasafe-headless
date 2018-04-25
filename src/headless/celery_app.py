# coding=utf-8
import os
import qgis  # noqa

from celery import Celery
from headless.settings import OUTPUT_DIRECTORY

__copyright__ = "Copyright 2018, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


def start_inasafe(locale='en_US'):
    """Initializa QGIS application and prepare InaSAFE settings.

    :param locale: Locale to be used for the analysis.
    :type locale: str

    :return: Tuple of QGIS application object and IFACE.
    :rtype: tuple
    """
    # Initialize qgis_app
    from safe.test.utilities import get_qgis_app
    QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app(locale)

    # Load QGIS Expression
    from safe.utilities.expressions import qgis_expressions  # noqa
    # Setting
    from safe.utilities.settings import set_setting

    if OUTPUT_DIRECTORY:
        try:
            os.makedirs(OUTPUT_DIRECTORY)
        except OSError:
            if not os.path.isdir(OUTPUT_DIRECTORY):
                raise
        set_setting('defaultUserDirectory', OUTPUT_DIRECTORY)

    return QGIS_APP, IFACE


app = Celery('headless.tasks')
app.config_from_object('headless.celeryconfig')

packages = (
    'headless',
)

app.autodiscover_tasks(packages)

if __name__ == '__main__':
    app.worker_main()
