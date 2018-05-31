# coding=utf-8
import os
import qgis  # noqa

from celery import Celery
from headless.settings import OUTPUT_DIRECTORY
from raven import Client
from raven.contrib.celery import register_signal, register_logger_signal

__copyright__ = "Copyright 2018, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


def start_inasafe(locale='en_US'):
    """Initialize QGIS application and prepare InaSAFE settings.

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


class SentryCelery(Celery):

    def on_configure(self):
        client = Client(
            'http://25f76b1f231344238fa740ef19a24f41:'
            '4965f3b1f30b4ad89ed56c1276f3250a@sentry.kartoza.com/12')

        # register a custom filter to filter out duplicate logs
        register_logger_signal(client)

        # hook into the Celery error handler
        register_signal(client)


app = SentryCelery('headless.tasks')
app.config_from_object('headless.celeryconfig')

packages = (
    'headless',
)

app.autodiscover_tasks(packages)

if __name__ == '__main__':
    app.worker_main()
