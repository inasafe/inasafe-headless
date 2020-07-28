# coding=utf-8
import os
import unittest
from distutils.util import strtobool

from headless.settings import OUTPUT_DIRECTORY
from headless.tasks.inasafe_wrapper import (
    run_analysis,
    run_multi_exposure_analysis,
    generate_report,
)
from headless.tasks.test.helpers import earthquake_layer_uri, \
    place_layer_uri, \
    aggregation_layer_uri, buildings_layer_uri, \
    population_multi_fields_layer_uri, buildings_layer_qlr_uri, \
    retry_on_worker_lost_error
from safe.definitions.constants import ANALYSIS_SUCCESS
from safe.definitions.layer_purposes import (
    layer_purpose_exposure_summary)
from safe.report.impact_report import ImpactReport
from safe.test.utilities import get_qgis_app

QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()

__copyright__ = "Copyright 2018, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


class TestRunAnalysis(unittest.TestCase):

    @retry_on_worker_lost_error()
    def test_run_analysis(self):
        """Test run analysis."""
        # With aggregation
        result_delay = run_analysis.delay(
            earthquake_layer_uri, place_layer_uri, aggregation_layer_uri)
        result = result_delay.get()
        self.assertEqual(ANALYSIS_SUCCESS, result['status'], result['message'])
        self.assertLess(0, len(result['output']))
        for key, layer_uri in result['output'].items():
            self.assertTrue(os.path.exists(layer_uri))
            self.assertTrue(layer_uri.startswith(OUTPUT_DIRECTORY))

        # No aggregation
        result_delay = run_analysis.delay(
            earthquake_layer_uri, place_layer_uri)
        result = result_delay.get()
        self.assertEqual(ANALYSIS_SUCCESS, result['status'], result['message'])
        self.assertLess(0, len(result['output']))
        for key, layer_uri in result['output'].items():
            self.assertTrue(os.path.exists(layer_uri))
            self.assertTrue(layer_uri.startswith(OUTPUT_DIRECTORY))

    @retry_on_worker_lost_error()
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
        self.assertEqual(ANALYSIS_SUCCESS, result['status'], result['message'])
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
        self.assertEqual(ANALYSIS_SUCCESS, result['status'], result['message'])
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

    @unittest.skipIf(
        strtobool(os.environ.get('ON_TRAVIS', 'False')),
        """Skipped because we don't have remote service QLR anymore.""")
    @retry_on_worker_lost_error()
    def test_run_analysis_qlr(self):
        """Test running analysis with QLR files."""
        # With aggregation
        result_delay = run_analysis.delay(
            earthquake_layer_uri, buildings_layer_qlr_uri,
            aggregation_layer_uri)
        result = result_delay.get()
        self.assertEqual(ANALYSIS_SUCCESS, result['status'],
                         result['message'])
        self.assertLess(0, len(result['output']))
        for key, layer_uri in result['output'].items():
            self.assertTrue(os.path.exists(layer_uri))
            self.assertTrue(layer_uri.startswith(OUTPUT_DIRECTORY))

        # No aggregation
        result_delay = run_analysis.delay(
            earthquake_layer_uri, buildings_layer_qlr_uri)
        result = result_delay.get()
        self.assertEqual(ANALYSIS_SUCCESS, result['status'],
                         result['message'])
        self.assertLess(0, len(result['output']))
        for key, layer_uri in result['output'].items():
            self.assertTrue(os.path.exists(layer_uri))
            self.assertTrue(layer_uri.startswith(OUTPUT_DIRECTORY))

    @retry_on_worker_lost_error()
    def test_run_multilingual_analysis(self):
        """Test run analysis."""

        # english analysis
        result_delay = run_analysis.delay(
            earthquake_layer_uri, place_layer_uri)
        result = result_delay.get()
        self.assertEqual(ANALYSIS_SUCCESS, result['status'], result['message'])
        self.assertLess(0, len(result['output']))
        for key, layer_uri in result['output'].items():
            self.assertTrue(os.path.exists(layer_uri))
            self.assertTrue(layer_uri.startswith(OUTPUT_DIRECTORY))

        # Retrieve impact analysis uri
        impact_analysis_uri_en = result['output'][
            layer_purpose_exposure_summary['key']]

        # english report

        # Add custom layers order for map report
        custom_layer_order = [
            impact_analysis_uri_en, earthquake_layer_uri
        ]

        # Generate reports
        async_result = generate_report.delay(
            impact_analysis_uri_en, custom_layer_order=custom_layer_order)
        result = async_result.get()
        self.assertEqual(
            ImpactReport.REPORT_GENERATION_SUCCESS, result['status'])
        for key, products in result['output'].items():
            for product_key, product_uri in products.items():
                message = 'Product %s is not found in %s' % (
                    product_key, product_uri)
                self.assertTrue(os.path.exists(product_uri), message)

        # Bahasa Indonesia analysis
        result_delay = run_analysis.delay(
            earthquake_layer_uri, place_layer_uri, locale='id')
        result = result_delay.get()
        self.assertEqual(ANALYSIS_SUCCESS, result['status'], result['message'])
        self.assertLess(0, len(result['output']))
        for key, layer_uri in result['output'].items():
            self.assertTrue(os.path.exists(layer_uri))
            self.assertTrue(layer_uri.startswith(OUTPUT_DIRECTORY))

        # Retrieve impact analysis uri
        impact_analysis_uri_id = result['output'][
            layer_purpose_exposure_summary['key']]

        # Bahasa Indonesia report

        # Add custom layers order for map report
        custom_layer_order = [
            impact_analysis_uri_id, earthquake_layer_uri
        ]

        # Generate reports
        async_result = generate_report.delay(
            impact_analysis_uri_id,
            custom_layer_order=custom_layer_order,
            locale='id')
        result = async_result.get()
        self.assertEqual(
            ImpactReport.REPORT_GENERATION_SUCCESS, result['status'])
        for key, products in result['output'].items():
            for product_key, product_uri in products.items():
                message = 'Product %s is not found in %s' % (
                    product_key, product_uri)
                self.assertTrue(os.path.exists(product_uri), message)
