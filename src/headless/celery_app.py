# coding=utf-8
import importlib
import json
import os

from celery import Celery
from headless import settings as headless_settings
from raven import Client
from raven.contrib.celery import register_signal, register_logger_signal

from headless.utils import set_logger, get_headless_logger
from safe.gui.tools.minimum_needs.needs_profile import NeedsProfile
from safe.utilities.settings import import_setting

__copyright__ = "Copyright 2018, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


LOGGER = get_headless_logger()


def load_inasafe_settings():
    """Load InaSAFE settings.

    File to load is given from environment variable.
    """
    # Load default settings
    from safe.definitions import default_settings
    from safe.utilities.settings import set_setting

    for key, value in default_settings.inasafe_default_settings.iteritems():
        set_setting(key, value)

    # Override settings from INASAFE_SETTINGS_PATH
    if headless_settings.INASAFE_SETTINGS_PATH:
        # Load from custom headless settings
        import_setting(headless_settings.INASAFE_SETTINGS_PATH)


def load_minimum_needs(locale='en_US'):
    """Load Minimum Needs profile.

    Profile to load is given from environment variable.
    """
    minimum_needs_path = None

    if headless_settings.MINIMUM_NEEDS_LOCALE_MAPPING_PATH:
        with open(headless_settings.MINIMUM_NEEDS_LOCALE_MAPPING_PATH) as f:
            locale_mapping = json.load(f)

        if locale in locale_mapping:
            minimum_needs_path = locale_mapping.get(locale, '')

            # Check if it is a relative path
            if not minimum_needs_path.startswith('/'):
                # The file specified in mapping file should be relative to
                # this mapping file itself
                mapping_dir_path = os.path.dirname(
                    headless_settings.MINIMUM_NEEDS_LOCALE_MAPPING_PATH)
                minimum_needs_path = os.path.join(
                    mapping_dir_path, minimum_needs_path)

    profile = NeedsProfile()
    if minimum_needs_path:
        try:
            profile.read_from_file(minimum_needs_path)
        except BaseException as e:
            LOGGER.debug(e)
            profile.minimum_needs = profile._defaults()
    else:
        # if no path specified, use internal minimum needs
        profile.minimum_needs = profile._defaults()

    profile.save()


def reload_definitions():
    """Brute force reload all related InaSAFE definitions to apply
    current locale."""
    package_list = [
        # Reload minimum needs
        'safe.definitions.minimum_needs',
        # Reload everything that depends on minimum_needs
        'safe.definitions.fields',
        'safe.definitions',

        # Reload min needs postprocessors
        'safe.processors.minimum_needs_post_processors',
        # Reload everything that depends on postprocessors
        'safe.processors',
        'safe.impact_function.postprocessors',
        'safe.impact_function',

        # Reload everything that depends on reporting
        'safe.report.extractors.aggregate_postprocessors',
        'safe.report.extractors.minimum_needs',
        'safe.report'
    ]
    for p in package_list:
        reload(importlib.import_module(p))

    from safe.definitions import minimum_needs
    from safe import processors
    LOGGER.debug('Minimum Needs list:')
    for m in minimum_needs.minimum_needs_fields:
        LOGGER.debug(m)

    LOGGER.debug('Minimum Needs Processors list:')
    for m in processors.minimum_needs_post_processors:
        LOGGER.debug(m)


def start_inasafe(locale='en_US'):
    """Initialize QGIS application and prepare InaSAFE settings.

    :param locale: Locale to be used for the analysis.
    :type locale: str

    :return: Tuple of QGIS application object and IFACE.
    :rtype: tuple
    """
    set_logger()

    # Initialize qgis_app
    from safe.test.utilities import get_qgis_app, set_canvas_crs
    QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app(locale)

    set_canvas_crs(4326, True)

    # Setting
    from safe.utilities.settings import set_setting

    # Reload default settings first
    from safe.definitions import default_settings
    from safe.utilities import settings
    reload(default_settings)
    reload(settings)
    reload(headless_settings)

    load_inasafe_settings()
    load_minimum_needs(locale)

    # reload minimum needs definitions
    # redeclarations are needed for report
    reload_definitions()

    # Load QGIS Expression
    # noinspection PyUnresolvedReferences
    from safe.utilities.expressions import qgis_expressions  # noqa

    if headless_settings.OUTPUT_DIRECTORY:
        try:
            os.makedirs(headless_settings.OUTPUT_DIRECTORY)
        except OSError:
            if not os.path.isdir(headless_settings.OUTPUT_DIRECTORY):
                raise
        set_setting(
            'defaultUserDirectory', headless_settings.OUTPUT_DIRECTORY)

    return QGIS_APP, IFACE


class SentryCelery(Celery):

    def on_configure(self):
        if headless_settings.ENABLE_SENTRY:
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
