# coding=utf-8
"""Unit test for celery task."""

import os
import unittest
from headless.tasks.inasafe_wrapper import get_keywords

from safe.definitions.layer_purposes import layer_purpose_exposure
from safe.definitions.exposure import exposure_place


dir_path = os.path.dirname(os.path.realpath(__file__))


class TestHeadlessCeleryTask(unittest.TestCase):
    """Unit test for Headless Celery tasks."""

    def test_get_keywords(self):
        """Test get_keywords task."""
        layer_path = os.path.join(dir_path, 'data', 'places.geojson')
        print layer_path
        self.assertTrue(os.path.exists(layer_path))
        result = get_keywords.delay(layer_path)
        keywords = result.get()
        self.assertIsNotNone(keywords)
        self.assertEqual(
            keywords['layer_purpose'], layer_purpose_exposure['key'])
        self.assertEqual(keywords['exposure'], exposure_place['key'])
