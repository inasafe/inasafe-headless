# coding=utf-8
import os
import unittest
from distutils.util import strtobool

from headless.settings import OUTPUT_DIRECTORY
from headless.tasks.inasafe_analysis import (
    REPORT_METADATA_NOT_EXIST,
    REPORT_METADATA_EXIST,
)
from headless.tasks.inasafe_wrapper import (
    run_analysis,
    run_multi_exposure_analysis,
    generate_report,
    get_generated_report,
)
from headless.tasks.test.helpers import earthquake_layer_uri, \
    buildings_layer_qlr_uri, aggregation_layer_uri, place_layer_uri, \
    buildings_layer_uri, population_multi_fields_layer_uri, \
    custom_map_template, custom_map_template_basename, \
    retry_on_worker_lost_error
from safe.definitions.constants import ANALYSIS_SUCCESS
from safe.definitions.layer_purposes import (
    layer_purpose_exposure_summary,
    layer_purpose_analysis_impacted)
from safe.report.impact_report import ImpactReport
from safe.test.utilities import get_qgis_app

QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()

__copyright__ = "Copyright 2018, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


class TestGenerateReport(unittest.TestCase):

    @unittest.skipIf(
        strtobool(os.environ.get('ON_TRAVIS', 'False')),
        """Skipped because we don't have remote service QLR anymore.""")
    @retry_on_worker_lost_error()
    def test_generate_report_qlr(self):
        """Test generating report with QLR files."""
        # With aggregation

        # Run analysis first
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

        # Retrieve impact analysis uri
        impact_analysis_uri = result['output'][
            layer_purpose_exposure_summary['key']]

        # Add custom layers order for map report
        custom_layer_order = [
            impact_analysis_uri, aggregation_layer_uri, earthquake_layer_uri
        ]

        # Generate reports
        async_result = generate_report.delay(
            impact_analysis_uri, custom_layer_order=custom_layer_order)
        result = async_result.get()
        self.assertEqual(
            ImpactReport.REPORT_GENERATION_SUCCESS, result['status'])
        for key, products in result['output'].items():
            for product_key, product_uri in products.items():
                message = 'Product %s is not found in %s' % (
                    product_key, product_uri)
                self.assertTrue(os.path.exists(product_uri), message)

    @retry_on_worker_lost_error()
    def test_generate_report_with_aggregation(self):
        """Test generate report for single analysis using aggregation layer.
        """

        # Run analysis first
        result_delay = run_analysis.delay(
            earthquake_layer_uri, place_layer_uri, aggregation_layer_uri)
        result = result_delay.get()
        self.assertEqual(ANALYSIS_SUCCESS, result['status'], result['message'])
        self.assertLess(0, len(result['output']))
        for key, layer_uri in result['output'].items():
            self.assertTrue(os.path.exists(layer_uri))
            self.assertTrue(layer_uri.startswith(OUTPUT_DIRECTORY))

        # Retrieve impact analysis uri
        impact_analysis_uri = result['output'][
            layer_purpose_exposure_summary['key']]

        # Add custom layers order for map report
        custom_layer_order = [
            impact_analysis_uri, aggregation_layer_uri, earthquake_layer_uri
        ]

        # Generate reports
        async_result = generate_report.delay(
            impact_analysis_uri, custom_layer_order=custom_layer_order)
        result = async_result.get()
        self.assertEqual(
            ImpactReport.REPORT_GENERATION_SUCCESS, result['status'])
        for key, products in result['output'].items():
            for product_key, product_uri in products.items():
                message = 'Product %s is not found in %s' % (
                    product_key, product_uri)
                self.assertTrue(os.path.exists(product_uri), message)

    @retry_on_worker_lost_error()
    def test_generate_report_without_aggregation(self):
        """Test generate report for single analysis without aggregation layer.
        """

        # Run analysis first
        result_delay = run_analysis.delay(
            earthquake_layer_uri, place_layer_uri)
        result = result_delay.get()
        self.assertEqual(0, result['status'], result['message'])
        self.assertLess(0, len(result['output']))
        for key, layer_uri in result['output'].items():
            self.assertTrue(os.path.exists(layer_uri))
            self.assertTrue(layer_uri.startswith(OUTPUT_DIRECTORY))

        # Retrieve impact analysis uri
        impact_analysis_uri = result['output'][
            'impact_analysis']

        # Add custom layers order for map report
        custom_layer_order = [
            impact_analysis_uri, earthquake_layer_uri
        ]

        # Generate reports
        async_result = generate_report.delay(
            impact_analysis_uri, custom_layer_order=custom_layer_order)
        result = async_result.get()
        self.assertEqual(
            ImpactReport.REPORT_GENERATION_SUCCESS, result['status'])
        for key, products in result['output'].items():
            for product_key, product_uri in products.items():
                message = 'Product %s is not found in %s' % (
                    product_key, product_uri)
                self.assertTrue(os.path.exists(product_uri), message)

    @retry_on_worker_lost_error()
    def test_generate_multi_exposure_report(self):
        """Test generate multi exposure analysis report."""
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

        # Retrieve impact analysis uri
        impact_analysis_uri = result['output'][
            layer_purpose_analysis_impacted['key']]

        # Add custom layers order for map report
        custom_layer_order = [
            impact_analysis_uri, earthquake_layer_uri
        ]

        # Generate reports
        async_result = generate_report.delay(
            impact_analysis_uri, custom_layer_order=custom_layer_order)
        result = async_result.get()
        self.assertEqual(
            ImpactReport.REPORT_GENERATION_SUCCESS, result['status'])
        for key, products in result['output'].items():
            for product_key, product_uri in products.items():
                message = 'Product %s is not found in %s' % (
                    product_key, product_uri)
                self.assertTrue(os.path.exists(product_uri), message)

    @retry_on_worker_lost_error()
    def test_generate_custom_report(self):
        """Test generate custom report for single analysis."""
        # Run analysis first
        result_delay = run_analysis.delay(
            earthquake_layer_uri,
            population_multi_fields_layer_uri,
            aggregation_layer_uri
        )
        result = result_delay.get()
        self.assertEqual(ANALYSIS_SUCCESS, result['status'], result['message'])
        self.assertLess(0, len(result['output']))
        for key, layer_uri in result['output'].items():
            self.assertTrue(os.path.exists(layer_uri))
            self.assertTrue(layer_uri.startswith(OUTPUT_DIRECTORY))

        # Retrieve impact analysis uri
        impact_analysis_uri = result['output'][
            layer_purpose_exposure_summary['key']]

        # Generate reports
        async_result = generate_report.delay(
            impact_analysis_uri, custom_map_template)
        result = async_result.get()
        self.assertEqual(
            ImpactReport.REPORT_GENERATION_SUCCESS, result['status'])
        product_keys = []
        for key, products in result['output'].items():
            for product_key, product_uri in products.items():
                product_keys.append(product_key)
                message = 'Product %s is not found in %s' % (
                    product_key, product_uri)
                self.assertTrue(os.path.exists(product_uri), message)
                if custom_map_template_basename == product_key:
                    print product_uri

        # Check if custom map template found.
        self.assertIn(custom_map_template_basename, product_keys)
        # Check if the default map reports are not found
        self.assertNotIn('inasafe-map-report-portrait', product_keys)
        self.assertNotIn('inasafe-map-report-landscape', product_keys)

    @retry_on_worker_lost_error()
    def test_generate_report_with_basemap(self):
        """Test generate report with basemap."""
        # Run analysis first
        result_delay = run_analysis.delay(
            earthquake_layer_uri,
            population_multi_fields_layer_uri,
            aggregation_layer_uri
        )
        result = result_delay.get()
        self.assertEqual(ANALYSIS_SUCCESS, result['status'],
                         result['message'])
        self.assertLess(0, len(result['output']))
        for key, layer_uri in result['output'].items():
            self.assertTrue(os.path.exists(layer_uri))
            self.assertTrue(layer_uri.startswith(OUTPUT_DIRECTORY))

        # Retrieve impact analysis uri
        impact_analysis_uri = result['output'][
            layer_purpose_exposure_summary['key']]

        custom_layer_order = [
            # first will be on top
            impact_analysis_uri,
            # put basemap source uri with QGIS provider info
            'type=xyz&url=http://tile.openstreetmap.org/{z}/{x}/{y}.png'
            '|qgis_provider=wms',
        ]

        # Generate reports
        async_result = generate_report.delay(
            impact_analysis_uri,
            custom_layer_order=custom_layer_order,
            custom_legend_layer=custom_layer_order[:1])
        result = async_result.get()
        self.assertEqual(
            ImpactReport.REPORT_GENERATION_SUCCESS, result['status'])
        product_keys = []
        for key, products in result['output'].items():
            for product_key, product_uri in products.items():
                product_keys.append(product_key)
                message = 'Product %s is not found in %s' % (
                    product_key, product_uri)
                self.assertTrue(os.path.exists(product_uri), message)
                if custom_map_template_basename == product_key:
                    print product_uri

    @retry_on_worker_lost_error()
    def test_get_generated_report(self):
        """Test get generated report task."""
        # Run analysis first
        result_delay = run_analysis.delay(
            earthquake_layer_uri, place_layer_uri, aggregation_layer_uri)
        result = result_delay.get()
        self.assertEqual(ANALYSIS_SUCCESS, result['status'], result['message'])
        self.assertLess(0, len(result['output']))
        for key, layer_uri in result['output'].items():
            self.assertTrue(os.path.exists(layer_uri))
            self.assertTrue(layer_uri.startswith(OUTPUT_DIRECTORY))

        # Retrieve impact analysis uri
        impact_analysis_uri = result['output'][
            layer_purpose_exposure_summary['key']]

        # Get generated report (but it's not yet generated)
        async_result = get_generated_report.delay(impact_analysis_uri)
        result = async_result.get()
        self.assertEqual(REPORT_METADATA_NOT_EXIST, result['status'])
        self.assertEqual({}, result['output'])

        # Generate reports
        async_result = generate_report.delay(impact_analysis_uri)
        result = async_result.get()
        self.assertEqual(
            ImpactReport.REPORT_GENERATION_SUCCESS, result['status'])
        report_metadata = result['output']

        # Get generated report (now it's already generated)
        async_result = get_generated_report.delay(impact_analysis_uri)
        result = async_result.get()
        self.assertEqual(REPORT_METADATA_EXIST, result['status'])
        self.assertDictEqual(report_metadata, result['output'])
