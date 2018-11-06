# coding=utf-8
import os
import unittest

import mock
from qgis.core import QgsApplication

from headless.celery_app import start_inasafe
from headless.celeryconfig import task_always_eager
from headless.tasks.test.helpers import settings_path, \
    minimum_needs_mapping_path
from safe.gui.tools.minimum_needs.needs_profile import NeedsProfile
from safe.test.utilities import get_qgis_app
from safe.utilities.settings import setting

QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()

__copyright__ = "Copyright 2018, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


class TestSettingsLoader(unittest.TestCase):

    @unittest.skipUnless(
        task_always_eager,
        'This test is only relevant on sync mode')
    def test_changed_inasafe_settings(self):
        """Test settings change are resolved correctly."""
        # Triggering start_inasafe should have reinitialized
        # Headless environment

        # Check default value
        patched_env = {
            'INASAFE_SETTINGS_PATH': ''
        }
        with mock.patch.dict(os.environ, patched_env):
            start_inasafe()

            # Should follow default settings
            self.assertEqual(
                os.path.join(
                    QgsApplication.qgisSettingsDirPath(),
                    'inasafe', 'metadata.db'),
                setting('keywordCachePath'))

        # mock environment variable
        patched_env = {
            'INASAFE_SETTINGS_PATH': settings_path
        }
        with mock.patch.dict(os.environ, patched_env):
            start_inasafe()

            self.assertEqual(
                '/Users/lucernae/.inasafe/keywords.db',
                setting('keywordCachePath'))

            self.assertEqual(
                setting('reportDisclaimer'),
                'om telolet om. kasih telolet yaaa.')

        # now, it should go back
        patched_env = {
            'INASAFE_SETTINGS_PATH': ''
        }
        with mock.patch.dict(os.environ, patched_env):
            start_inasafe()

            self.assertEqual(
                os.path.join(
                    QgsApplication.qgisSettingsDirPath(),
                    'inasafe', 'metadata.db'),
                setting('keywordCachePath'))

    @unittest.skipUnless(
        task_always_eager,
        'This test is only relevant on sync mode')
    def test_minimum_needs_switching(self):
        """Test correct minimum needs is used."""
        # Check default minimum needs
        patched_env = {
            'MINIMUM_NEEDS_LOCALE_MAPPING_PATH': ''
        }
        with mock.patch.dict(os.environ, patched_env):
            start_inasafe('en')

            profile = NeedsProfile()
            profile.load()

            self.assertEqual('en', profile.locale)
            self.assertEqual('BNPB_en', profile.minimum_needs['profile'])
            self.assertEqual(
                'The minimum needs are based on Perka 7/2008.',
                profile.provenance)

        # mock environment variable
        patched_env = {
            'MINIMUM_NEEDS_LOCALE_MAPPING_PATH': minimum_needs_mapping_path
        }
        with mock.patch.dict(os.environ, patched_env):
            start_inasafe('id')

            profile = NeedsProfile()
            profile.load()

            self.assertEqual('id', profile.locale)
            self.assertEqual('BNPB_id', profile.minimum_needs['profile'])
            self.assertEqual(
                'Standar kebutuhan dasar ini berdasarkan pada '
                'Perka BNPB no.7 tahun 2008.',
                profile.provenance)

            # unknown locale will default to default minimum needs
            start_inasafe('es')

            profile = NeedsProfile()
            profile.load()

            self.assertEqual('es', profile.locale)
            self.assertEqual('BNPB_en', profile.minimum_needs['profile'])
            self.assertEqual(
                'The minimum needs are based on Perka 7/2008.',
                profile.provenance)

        # Should be back to default
        patched_env = {
            'MINIMUM_NEEDS_LOCALE_MAPPING_PATH': ''
        }
        with mock.patch.dict(os.environ, patched_env):
            start_inasafe('en')

            profile = NeedsProfile()
            profile.load()

            self.assertEqual('en', profile.locale)
            self.assertEqual('BNPB_en', profile.minimum_needs['profile'])
            self.assertEqual(
                'The minimum needs are based on Perka 7/2008.',
                profile.provenance)
