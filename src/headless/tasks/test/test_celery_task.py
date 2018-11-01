# coding=utf-8
"""Unit test for celery task."""
import os
import pickle
import unittest

from headless.settings import OUTPUT_DIRECTORY
from headless.tasks.inasafe_analysis import (
    clean_metadata,
    QUrl,
)
from headless.tasks.inasafe_wrapper import (
    get_keywords,
    generate_contour,
    check_broker_connection,
)
from headless.tasks.test.helpers import \
    place_layer_uri, earthquake_layer_uri, \
    aggregation_layer_uri, buildings_layer_qlr_uri, shakemap_layer_uri, \
    retry_on_worker_lost_error
from safe.definitions import exposure_structure
from safe.definitions.exposure import exposure_place
from safe.definitions.extra_keywords import extra_keyword_time_zone
from safe.definitions.hazard import hazard_earthquake
from safe.definitions.layer_purposes import (
    layer_purpose_exposure,
    layer_purpose_hazard,
    layer_purpose_aggregation)
from safe.test.utilities import get_qgis_app

QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()

__copyright__ = "Copyright 2018, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


class TestHeadlessCeleryTask(unittest.TestCase):
    """Unit test for Headless Celery tasks."""

    @retry_on_worker_lost_error()
    def test_get_keywords(self):
        """Test get_keywords task."""
        self.assertTrue(os.path.exists(place_layer_uri))
        result = get_keywords.delay(place_layer_uri)
        keywords = result.get()
        self.assertIsNotNone(keywords)
        self.assertEqual(
            keywords['layer_purpose'], layer_purpose_exposure['key'])
        self.assertEqual(keywords['exposure'], exposure_place['key'])

        # Test retrieve specific keyword
        result = get_keywords.delay(
            place_layer_uri, keyword='layer_purpose')
        keyword = result.get()
        self.assertIsNotNone(keyword)
        self.assertEqual(keyword, layer_purpose_exposure['key'])

        pickled_keywords = pickle.dumps(keywords)
        new_keywords = pickle.loads(pickled_keywords)
        self.assertDictEqual(keywords, new_keywords)

        self.assertTrue(os.path.exists(earthquake_layer_uri))
        result = get_keywords.delay(earthquake_layer_uri)
        keywords = result.get()
        self.assertIsNotNone(keywords)
        self.assertEqual(
            keywords['layer_purpose'], layer_purpose_hazard['key'])
        self.assertEqual(keywords['hazard'], hazard_earthquake['key'])
        time_zone = keywords['extra_keywords'][extra_keyword_time_zone['key']]
        self.assertEqual(time_zone, 'Asia/Jakarta')

        pickled_keywords = pickle.dumps(keywords)
        new_keywords = pickle.loads(pickled_keywords)
        self.assertDictEqual(keywords, new_keywords)

        self.assertTrue(os.path.exists(aggregation_layer_uri))
        result = get_keywords.delay(aggregation_layer_uri)
        keywords = result.get()
        self.assertIsNotNone(keywords)
        self.assertEqual(
            keywords['layer_purpose'], layer_purpose_aggregation['key'])

        pickled_keywords = pickle.dumps(keywords)
        new_keywords = pickle.loads(pickled_keywords)
        self.assertDictEqual(keywords, new_keywords)

        # Test loading QLR layer will also load keywords from xml file if
        # possible
        self.assertTrue(os.path.exists(buildings_layer_qlr_uri))
        result = get_keywords.delay(buildings_layer_qlr_uri)
        keywords = result.get()
        self.assertIsNotNone(keywords)
        self.assertEqual(
            keywords['layer_purpose'], layer_purpose_exposure['key'])
        self.assertEqual(keywords['exposure'], exposure_structure['key'])

    @retry_on_worker_lost_error()
    def test_generate_contour(self):
        """Test generate_contour task."""
        # Layer
        result_delay = generate_contour.delay(shakemap_layer_uri)
        result = result_delay.get()
        self.assertIsNotNone(result)
        self.assertTrue(os.path.exists(result))
        self.assertTrue(result.startswith(OUTPUT_DIRECTORY))

    @retry_on_worker_lost_error()
    def test_check_broker_connection(self):
        """Test check_broker_connection task."""
        async_result = check_broker_connection.delay()
        result = async_result.get()
        self.assertTrue(result)

    def test_clean_metadata(self):
        """Test clean_metadata method."""
        metadata = {
            'layer_purpose': 'hazard',
            'extra_keywords': {
                'url': QUrl('google.com')
            },
            'url': QUrl('kartoza.com')
        }
        self.assertTrue(isinstance(metadata['url'], QUrl))
        self.assertTrue(
            isinstance(metadata['extra_keywords']['url'], QUrl))
        clean_metadata(metadata)
        self.assertTrue(isinstance(metadata['url'], basestring))
        self.assertTrue(
            isinstance(metadata['extra_keywords']['url'], basestring))
