# coding=utf-8
"""Unit test for celery task."""
import os
import pickle
import unittest

from qgis.core import QgsMapLayerRegistry

from headless.celeryconfig import task_always_eager
from headless.settings import OUTPUT_DIRECTORY, PUSH_TO_REALTIME_GEONODE
from headless.tasks.inasafe_analysis import (
    clean_metadata,
    QUrl,
    REPORT_METADATA_NOT_EXIST,
    REPORT_METADATA_EXIST,
    GEONODE_UPLOAD_SUCCESS,
    GEONODE_UPLOAD_FAILED,
)
from headless.tasks.inasafe_wrapper import (
    get_keywords,
    run_analysis,
    generate_contour,
    run_multi_exposure_analysis,
    generate_report,
    get_generated_report,
    check_broker_connection,
    push_to_geonode,
)
from safe.definitions import exposure_structure
from safe.definitions.constants import ANALYSIS_SUCCESS
from safe.definitions.exposure import exposure_place
from safe.definitions.extra_keywords import extra_keyword_time_zone
from safe.definitions.hazard import hazard_earthquake
from safe.definitions.layer_purposes import (
    layer_purpose_exposure,
    layer_purpose_hazard,
    layer_purpose_aggregation,
    layer_purpose_exposure_summary,
    layer_purpose_analysis_impacted)
from safe.report.impact_report import ImpactReport
from safe.test.utilities import get_qgis_app, standard_data_path

QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()

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
buildings_layer_qlr_uri = os.path.join(
    dir_path, 'data', 'input_layers', 'buildings.qlr')

shapefile_layer_uri = standard_data_path('exposure', 'airports.shp')
ascii_layer_uri = standard_data_path('gisv4', 'hazard', 'earthquake.asc')
tif_layer_uri = standard_data_path('hazard', 'earthquake.tif')
geojson_layer_uri = standard_data_path(
    'gisv4', 'hazard', 'classified_vector.geojson')

# Map template
custom_map_template_basename = 'custom-inasafe-map-report-landscape'
custom_map_template = os.path.join(
    dir_path, 'data', custom_map_template_basename + '.qpt'
)


# Common message
geonode_disabled_message = (
    'Only run this test if we set the PUSH_TO_REALTIME_GEONODE variable to '
    'True.')


class TestHeadlessCeleryTask(unittest.TestCase):
    """Unit test for Headless Celery tasks."""

    def check_layer_registry_empty(self):
        # Layer registry should be empty between run
        layer_registry = QgsMapLayerRegistry.instance()
        self.assertDictEqual(layer_registry.mapLayers(), {})

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

    def test_generate_contour(self):
        """Test generate_contour task."""
        # Layer
        result_delay = generate_contour.delay(shakemap_layer_uri)
        result = result_delay.get()
        self.assertIsNotNone(result)
        self.assertTrue(os.path.exists(result))
        self.assertTrue(result.startswith(OUTPUT_DIRECTORY))

    def test_generate_report_with_aggregation(self):
        """Test generate report for single analysis using aggregation layer."""

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

    @unittest.skipUnless(
        task_always_eager,
        'This task only makes sense when it was tested on the same thread.'
        'It will be skipped on async Celery test, because the validity check'
        ' was on different QGIS Instance, thus will always be success '
        '(and useless) on that setup.'
    )
    def test_layer_registry_empty_on_subsequent_run(self):
        """Test layer registry were properly cleaned up

        More about this test.
        We are testing that a subsequent run of analysis or multi exposure
        analysis or report generation will properly cleanup QGIS Layer
        registry.
        This is because the same QGIS instance is used on the same thread,
        but different if it is on a different thread. We have to make sure
        each new analysis or report generation is a fresh one.

        Assuming other unittests were checking on each task validity, then
        this method will only test the state of layer registry between each
        task to avoid test duplication.
        """
        # It should be empty at first, if not, other tests is changing the
        # state
        self.check_layer_registry_empty()

        ######################################################################
        # Run single analysis
        #   With aggregation
        result_delay = run_analysis.delay(
            earthquake_layer_uri, place_layer_uri, aggregation_layer_uri)
        result = result_delay.get()

        # It should be empty, if not, above test didn't cleanup
        self.check_layer_registry_empty()

        #       Retrieve impact analysis uri
        impact_analysis_uri = result['output'][
            layer_purpose_exposure_summary['key']]

        #       Add custom layers order for map report
        custom_layer_order = [
            impact_analysis_uri, aggregation_layer_uri, earthquake_layer_uri
        ]

        #   Generate reports
        async_result = generate_report.delay(
            impact_analysis_uri, custom_layer_order=custom_layer_order)
        result = async_result.get()

        # It should be empty, if not, above test didn't cleanup
        self.check_layer_registry_empty()

        #   No aggregation
        result_delay = run_analysis.delay(
            earthquake_layer_uri, place_layer_uri)
        result = result_delay.get()

        # It should be empty, if not, above test didn't cleanup
        self.check_layer_registry_empty()

        #       Retrieve impact analysis uri
        impact_analysis_uri = result['output'][
            layer_purpose_exposure_summary['key']]

        #       Add custom layers order for map report
        custom_layer_order = [
            impact_analysis_uri, earthquake_layer_uri
        ]

        #   Generate reports
        async_result = generate_report.delay(
            impact_analysis_uri, custom_layer_order=custom_layer_order)
        result = async_result.get()

        # It should be empty, if not, above test didn't cleanup
        self.check_layer_registry_empty()
        ######################################################################

        ######################################################################
        # Run multi exposure analysis
        exposure_layer_uris = [
            place_layer_uri,
            buildings_layer_uri,
            population_multi_fields_layer_uri
        ]
        #   With aggregation
        result_delay = run_multi_exposure_analysis.delay(
            earthquake_layer_uri, exposure_layer_uris, aggregation_layer_uri)
        result = result_delay.get()

        # It should be empty, if not, above test didn't cleanup
        self.check_layer_registry_empty()

        #       Retrieve impact analysis uri
        impact_analysis_uri = result['output'][
            layer_purpose_analysis_impacted['key']]

        #       Add custom layers order for map report
        custom_layer_order = [
            impact_analysis_uri, aggregation_layer_uri, earthquake_layer_uri
        ]

        #   Generate reports
        async_result = generate_report.delay(
            impact_analysis_uri, custom_layer_order=custom_layer_order)
        result = async_result.get()

        # It should be empty, if not, above test didn't cleanup
        self.check_layer_registry_empty()

        #   No aggregation
        result_delay = run_multi_exposure_analysis.delay(
            earthquake_layer_uri, exposure_layer_uris)
        result = result_delay.get()

        # It should be empty, if not, above test didn't cleanup
        self.check_layer_registry_empty()

        #       Retrieve impact analysis uri
        impact_analysis_uri = result['output'][
            layer_purpose_analysis_impacted['key']]

        #       Add custom layers order for map report
        custom_layer_order = [
            impact_analysis_uri, earthquake_layer_uri
        ]

        #   Generate reports
        async_result = generate_report.delay(
            impact_analysis_uri, custom_layer_order=custom_layer_order)
        result = async_result.get()

        # It should be empty, if not, above test didn't cleanup
        self.check_layer_registry_empty()

        #   Generate custom reports
        async_result = generate_report.delay(
            impact_analysis_uri, custom_map_template)
        result = async_result.get()

        # It should be empty, if not, above test didn't cleanup
        self.check_layer_registry_empty()

    @unittest.skipUnless(PUSH_TO_REALTIME_GEONODE, geonode_disabled_message)
    def test_push_shapefile_to_geonode(self):
        """Test push shapefile layer to geonode functionality."""
        async_result = push_to_geonode.delay(shapefile_layer_uri)
        result = async_result.get()
        self.assertEqual(
            result['status'], GEONODE_UPLOAD_SUCCESS, result['message'])

    @unittest.skipUnless(PUSH_TO_REALTIME_GEONODE, geonode_disabled_message)
    def test_push_tif_to_geonode(self):
        """Test push tif layer to geonode functionality."""
        async_result = push_to_geonode.delay(tif_layer_uri)
        result = async_result.get()
        self.assertEqual(
            result['status'], GEONODE_UPLOAD_SUCCESS, result['message'])

    @unittest.skipUnless(PUSH_TO_REALTIME_GEONODE, geonode_disabled_message)
    def test_push_ascii_to_geonode(self):
        """Test push ascii layer to geonode functionality."""
        async_result = push_to_geonode.delay(ascii_layer_uri)
        result = async_result.get()
        self.assertEqual(
            result['status'], GEONODE_UPLOAD_SUCCESS, result['message'])

    @unittest.skipUnless(PUSH_TO_REALTIME_GEONODE, geonode_disabled_message)
    def test_push_geojson_to_geonode(self):
        """Test push geojson layer to geonode functionality."""
        async_result = push_to_geonode.delay(geojson_layer_uri)
        result = async_result.get()
        self.assertEqual(
            result['status'], GEONODE_UPLOAD_SUCCESS, result['message'])

    @unittest.skipUnless(PUSH_TO_REALTIME_GEONODE, geonode_disabled_message)
    def test_push_to_geonode_failed(self):
        """Test push to geonode functionality."""
        async_result = push_to_geonode.delay(
            shakemap_layer_uri,
            geonode_user='NotUser',
            geonode_password='NotPassword')
        result = async_result.get()
        self.assertEqual(result['status'], GEONODE_UPLOAD_FAILED)
        self.assertTrue('Failed to login' in result['message'])
