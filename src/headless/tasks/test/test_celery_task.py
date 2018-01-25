# coding=utf-8
"""Unit test for celery task."""

import os
import unittest
from headless.tasks.inasafe_wrapper import (
    get_keywords,
    run_analysis,
    generate_contour,
    run_multi_exposure_analysis
)
from headless.settings import OUTPUT_DIRECTORY

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

# Layers
earthquake_layer_uri = os.path.join(
    dir_path, 'data', 'input_layers', 'earthquake.asc')
shakemap_layer_uri = os.path.join(
    dir_path, 'data', 'input_layers', 'grid-use_ascii.tif')
place_layer_uri = os.path.join(
    dir_path, 'data', 'input_layers', 'places.geojson')
aggregation_layer_uri = os.path.join(
    dir_path, 'data', 'input_layers', 'small_grid.geojson')
population_multi_fields_layer_uri = os.path.join(
    dir_path, 'data', 'input_layers', 'population_multi_fields.geojson')
buildings_layer_uri = os.path.join(
    dir_path, 'data', 'input_layers', 'buildings.geojson')


class TestHeadlessCeleryTask(unittest.TestCase):
    """Unit test for Headless Celery tasks."""

    def test_get_keywords(self):
        """Test get_keywords task."""
        self.assertTrue(os.path.exists(place_layer_uri))
        result = get_keywords.delay(place_layer_uri)
        keywords = result.get()
        self.assertIsNotNone(keywords)
        self.assertEqual(
            keywords['layer_purpose'], layer_purpose_exposure['key'])
        self.assertEqual(keywords['exposure'], exposure_place['key'])

        self.assertTrue(os.path.exists(earthquake_layer_uri))
        result = get_keywords.delay(earthquake_layer_uri)
        keywords = result.get()
        self.assertIsNotNone(keywords)
        self.assertEqual(
            keywords['layer_purpose'], layer_purpose_hazard['key'])
        self.assertEqual(keywords['hazard'], hazard_earthquake['key'])
        time_zone = keywords['extra_keywords'][extra_keyword_time_zone['key']]
        self.assertEqual(time_zone, 'Asia/Jakarta')

        self.assertTrue(os.path.exists(aggregation_layer_uri))
        result = get_keywords.delay(aggregation_layer_uri)
        keywords = result.get()
        self.assertIsNotNone(keywords)
        self.assertEqual(
            keywords['layer_purpose'], layer_purpose_aggregation['key'])

    def test_run_analysis(self):
        """Test run analysis."""
        # With aggregation
        result_delay = run_analysis.delay(
            earthquake_layer_uri, place_layer_uri, aggregation_layer_uri)
        result = result_delay.get()
        self.assertEqual(ANALYSIS_SUCCESS, result['status'])
        self.assertLess(0, len(result['output']))
        for key, layer_uri in result['output'].items():
            self.assertTrue(os.path.exists(layer_uri))
            self.assertTrue(layer_uri.startswith(OUTPUT_DIRECTORY))

        # No aggregation
        result_delay = run_analysis.delay(
            earthquake_layer_uri, place_layer_uri)
        result = result_delay.get()
        self.assertEqual(ANALYSIS_SUCCESS, result['status'])
        self.assertLess(0, len(result['output']))
        for key, layer_uri in result['output'].items():
            self.assertTrue(os.path.exists(layer_uri))
            self.assertTrue(layer_uri.startswith(OUTPUT_DIRECTORY))

    def test_run_multi_exposure_analysis(self):
        """Test run multi_exposure analysis."""
        exposure_layer_uris = [
            place_layer_uri,
            buildings_layer_uri,
            population_multi_fields_layer_uri
        ]
        # With aggregation
        result_delay = run_multi_exposure_analysis.delay(
            earthquake_layer_uri, exposure_layer_uris, aggregation_layer_uri)
        result = result_delay.get()
        self.assertEqual(ANALYSIS_SUCCESS, result['status'])
        self.assertLess(0, len(result['output']))
        num_exposure_output = 0
        for key, layer_uri in result['output'].items():
            if isinstance(layer_uri, basestring):
                self.assertTrue(os.path.exists(layer_uri))
                self.assertTrue(layer_uri.startswith(OUTPUT_DIRECTORY))
            elif isinstance(layer_uri, dict):
                num_exposure_output += 1
                for the_key, the_layer_uri in layer_uri.items():
                    self.assertTrue(os.path.exists(the_layer_uri))
                    self.assertTrue(the_layer_uri.startswith(OUTPUT_DIRECTORY))
        # Check the number of per exposure output is the same as the number
        # of exposures
        self.assertEqual(num_exposure_output, len(exposure_layer_uris))

        # No aggregation
        result_delay = run_multi_exposure_analysis.delay(
            earthquake_layer_uri, exposure_layer_uris)
        result = result_delay.get()
        self.assertEqual(ANALYSIS_SUCCESS, result['status'])
        self.assertLess(0, len(result['output']))
        num_exposure_output = 0
        for key, layer_uri in result['output'].items():
            if isinstance(layer_uri, basestring):
                self.assertTrue(os.path.exists(layer_uri))
                self.assertTrue(layer_uri.startswith(OUTPUT_DIRECTORY))
            elif isinstance(layer_uri, dict):
                num_exposure_output += 1
                for the_key, the_layer_uri in layer_uri.items():
                    self.assertTrue(os.path.exists(the_layer_uri))
                    self.assertTrue(the_layer_uri.startswith(OUTPUT_DIRECTORY))
        # Check the number of per exposure output is the same as the number
        # of exposures
        self.assertEqual(num_exposure_output, len(exposure_layer_uris))

    def test_generate_contour_async(self):
        """Test generate_contour task."""
        # Layer
        result_delay = generate_contour.delay(shakemap_layer_uri)
        result = result_delay.get()
        self.assertIsNotNone(result)
        self.assertTrue(os.path.exists(result))
        self.assertTrue(result.startswith(OUTPUT_DIRECTORY))
