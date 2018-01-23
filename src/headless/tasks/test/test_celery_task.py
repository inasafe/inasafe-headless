# coding=utf-8
"""Unit test for celery task."""

import os
import unittest
from headless.tasks.inasafe_wrapper import get_keywords

from safe.definitions.layer_purposes import (
    layer_purpose_exposure, layer_purpose_hazard)
from safe.definitions.exposure import exposure_place
from safe.definitions.hazard import hazard_earthquake
from safe.definitions.extra_keywords import extra_keyword_time_zone


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
