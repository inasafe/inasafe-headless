# coding=utf-8
import os
import unittest

from qgis.core import QgsMapLayerRegistry

from headless.celeryconfig import task_always_eager
from headless.tasks.inasafe_wrapper import (
    run_analysis,
    run_multi_exposure_analysis,
    generate_report,
)
from headless.tasks.test.helpers import earthquake_layer_uri, \
    place_layer_uri, \
    aggregation_layer_uri, buildings_layer_uri, \
    population_multi_fields_layer_uri, custom_map_template, \
    retry_on_worker_lost_error
from safe.definitions.layer_purposes import (
    layer_purpose_exposure_summary,
    layer_purpose_analysis_impacted)
from safe.test.utilities import get_qgis_app

QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()

__copyright__ = "Copyright 2018, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


class TestSubsequentRun(unittest.TestCase):

    def check_layer_registry_empty(self):
        # Layer registry should be empty between run
        layer_registry = QgsMapLayerRegistry.instance()
        self.assertDictEqual(layer_registry.mapLayers(), {})

    @unittest.skipUnless(
        task_always_eager and os.environ.get('SUBSEQUENT_RUN_TESTING'),
        'This task only makes sense when it was tested on the same thread.'
        'It will be skipped on async Celery test, because the validity check'
        ' was on different QGIS Instance, thus will always be success '
        '(and useless) on that setup.'
    )
    @retry_on_worker_lost_error()
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
