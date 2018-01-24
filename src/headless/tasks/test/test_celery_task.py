# coding=utf-8
"""Unit test for celery task."""

import os
import unittest
from headless.tasks.inasafe_wrapper import (
    get_keywords, run_analysis, generate_contour)

from safe.definitions.layer_purposes import (
    layer_purpose_exposure, layer_purpose_hazard, layer_purpose_aggregation)
from safe.definitions.exposure import exposure_place
from safe.definitions.hazard import hazard_earthquake
from safe.definitions.extra_keywords import extra_keyword_time_zone
from safe.definitions.constants import ANALYSIS_SUCCESS

__copyright__ = "Copyright 2018, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


dir_path = os.path.dirname(os.path.realpath(__file__))


class TestHeadlessCeleryTask(unittest.TestCase):
    """Unit test for Headless Celery tasks."""

    def test_get_keywords(self):
        """Test get_keywords task."""
        layer_path = os.path.join(dir_path, 'data', 'places.geojson')
        self.assertTrue(os.path.exists(layer_path))
        result = get_keywords.delay(layer_path)
        keywords = result.get()
        self.assertIsNotNone(keywords)
        self.assertEqual(
            keywords['layer_purpose'], layer_purpose_exposure['key'])
        self.assertEqual(keywords['exposure'], exposure_place['key'])

        layer_path = os.path.join(dir_path, 'data', 'earthquake.asc')
        self.assertTrue(os.path.exists(layer_path))
        result = get_keywords.delay(layer_path)
        keywords = result.get()
        self.assertIsNotNone(keywords)
        self.assertEqual(
            keywords['layer_purpose'], layer_purpose_hazard['key'])
        self.assertEqual(keywords['hazard'], hazard_earthquake['key'])
        time_zone = keywords['extra_keywords'][extra_keyword_time_zone['key']]
        self.assertEqual(time_zone, 'Asia/Jakarta')

        layer_path = os.path.join(dir_path, 'data', 'small_grid.geojson')
        self.assertTrue(os.path.exists(layer_path))
        result = get_keywords.delay(layer_path)
        keywords = result.get()
        self.assertIsNotNone(keywords)
        self.assertEqual(
            keywords['layer_purpose'], layer_purpose_aggregation['key'])

    def test_run_analysis(self):
        """Test run analysis synchronously."""
        # Layers
        exposure_uri = os.path.join(dir_path, 'data', 'places.geojson')
        hazard_uri = os.path.join(dir_path, 'data', 'earthquake.asc')
        aggregation_uri = os.path.join(dir_path, 'data', 'small_grid.geojson')

        # With aggregation
        result = run_analysis(hazard_uri, exposure_uri, aggregation_uri)
        self.assertEqual(ANALYSIS_SUCCESS, result['status'])
        self.assertLess(0, len(result['output']))
        for key, layer_uri in result['output'].items():
            self.assertTrue(os.path.exists(layer_uri))

        # No aggregation
        result = run_analysis(hazard_uri, exposure_uri)
        self.assertEqual(ANALYSIS_SUCCESS, result['status'])
        self.assertLess(0, len(result['output']))
        for key, layer_uri in result['output'].items():
            self.assertTrue(os.path.exists(layer_uri))

    def test_run_analysis_async(self):
        """Test run analysis asynchronously."""
        # Layers
        exposure_uri = os.path.join(dir_path, 'data', 'places.geojson')
        hazard_uri = os.path.join(dir_path, 'data', 'earthquake.asc')
        aggregation_uri = os.path.join(dir_path, 'data', 'small_grid.geojson')

        # With aggregation
        result = run_analysis.delay(hazard_uri, exposure_uri, aggregation_uri)
        result_dict = result.get()
        self.assertEqual(ANALYSIS_SUCCESS, result_dict['status'])
        self.assertLess(0, len(result_dict['output']))
        for key, layer_uri in result_dict['output'].items():
            self.assertTrue(os.path.exists(layer_uri))

        # No aggregation
        result = run_analysis.delay(hazard_uri, exposure_uri)
        result_dict = result.get()
        self.assertEqual(ANALYSIS_SUCCESS, result_dict['status'])
        self.assertLess(0, len(result_dict['output']))
        for key, layer_uri in result_dict['output'].items():
            print key, layer_uri
            self.assertTrue(os.path.exists(layer_uri))

    def test_generate_contour(self):
        """Test generate_contour task synchronously."""
        # Layer
        shakemap_uri = os.path.join(dir_path, 'data', 'grid-use_ascii.tif')
        result = generate_contour(shakemap_uri)
        self.assertIsNotNone(result)
        self.assertTrue(os.path.exists(result))

    def test_generate_contour_async(self):
        """Test generate_contour task asynchronously."""
        # Layer
        shakemap_uri = os.path.join(dir_path, 'data', 'grid-use_ascii.tif')
        result = generate_contour.delay(shakemap_uri)
        contour_result = result.get()
        self.assertIsNotNone(contour_result)
        self.assertTrue(os.path.exists(contour_result))
