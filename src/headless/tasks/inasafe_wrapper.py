# coding=utf-8
"""Task for InaSAFE Headless."""
import json
import logging
import os
from datetime import datetime
from copy import deepcopy

from headless.celery_app import app

from PyQt4.QtCore import QUrl
from qgis.core import (
    QgsCoordinateReferenceSystem, QgsMapLayerRegistry, QgsProject)

from safe.definitions.constants import (
    PREPARE_SUCCESS, ANALYSIS_SUCCESS, MULTI_EXPOSURE_ANALYSIS_FLAG)
from safe.definitions.extra_keywords import extra_keyword_analysis_type
from safe.definitions.reports.components import (
    all_default_report_components, map_report)
from safe.definitions.utilities import override_component_template
from safe.gui.analysis_utilities import add_impact_layers_to_canvas
from safe.impact_function.impact_function import ImpactFunction
from safe.impact_function.impact_function_utilities import report_urls
from safe.impact_function.multi_exposure_wrapper import (
    MultiExposureImpactFunction)
from safe.gis.raster.contour import create_smooth_contour
from safe.gis.tools import load_layer
from safe.utilities.settings import setting
from safe.utilities.metadata import read_iso19115_metadata
from safe.gui.widgets.dock import set_provenance_to_project_variables

# Initialize qgis_app
from safe.test.utilities import get_qgis_app  # noqa
QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()

__copyright__ = "Copyright 2018, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'

LOGGER = logging.getLogger('InaSAFE Headless')

REPORT_METADATA_EXIST = 0
REPORT_METADATA_NOT_EXIST = 1


def clean_metadata(metadata):
    """Clean metadata's content from QUrl.

    :param metadata: Metadata as dictionary.
    :type metadata: dict
    """
    for key, value in metadata.items():
        if isinstance(value, dict):
            clean_metadata(value)
        if isinstance(value, QUrl):
            metadata[key] = value.toString()


@app.task(name='inasafe.headless.tasks.get_keywords', queue='inasafe-headless')
def get_keywords(layer_uri, keyword=None):
    """Get keywords from a layer.

    :param layer_uri: Uri to layer.
    :type layer_uri: basestring

    :param keyword: The key of keyword that want to be read. If None, return
        all keywords in dictionary.
    :type keyword: basestring

    :returns: Dictionary of keywords or value of key as string.
    :rtype: dict, basestring
    """
    metadata = read_iso19115_metadata(layer_uri, keyword)
    clean_metadata(metadata)
    return metadata


@app.task(name='inasafe.headless.tasks.run_analysis', queue='inasafe-headless')
def run_analysis(
        hazard_layer_uri,
        exposure_layer_uri,
        aggregation_layer_uri=None,
        crs=None
):
    """Run analysis.

    :param hazard_layer_uri: Uri to hazard layer.
    :type hazard_layer_uri: basestring

    :param exposure_layer_uri: Uri to exposure layer.
    :type exposure_layer_uri: basestring

    :param aggregation_layer_uri: Uri to aggregation layer.
    :type aggregation_layer_uri: basestring

    :param crs: CRS for the analysis (if the aggregation is not set).
    :param crs: QgsCoordinateReferenceSystem

    :returns: A dictionary of output's layer key and Uri with status and
        message.
    :rtype: dict

    The output format will be:
    output = {
        'status': 0,
        'message': '',
        'outputs': {
            'output_layer_key_1': 'output_layer_path_1',
            'output_layer_key_2': 'output_layer_path_2',
        }
    }
    """
    impact_function = ImpactFunction()
    impact_function.hazard = load_layer(hazard_layer_uri)[0]
    impact_function.exposure = load_layer(exposure_layer_uri)[0]
    if aggregation_layer_uri:
        impact_function.aggregation = load_layer(aggregation_layer_uri)[0]
    elif crs:
        impact_function.use_exposure_view_only = True
        impact_function.crs = crs
    else:
        impact_function.crs = QgsCoordinateReferenceSystem(4326)
    prepare_status, prepare_message = impact_function.prepare()
    if prepare_status == PREPARE_SUCCESS:
        LOGGER.debug('Impact function is ready')
        status, message = impact_function.run()
        if status == ANALYSIS_SUCCESS:
            outputs = impact_function.outputs
            output_dict = {}
            for layer in outputs:
                output_dict[layer.keywords['layer_purpose']] = layer.source()

            add_impact_layers_to_canvas(impact_function)

            return {
                'status': ANALYSIS_SUCCESS,
                'message': '',
                'output': output_dict
            }
        else:
            LOGGER.debug('Analysis failed %s' % message)
            return {
                'status': status,
                'message': message.to_text(),
                'output': {}
            }
    else:
        LOGGER.debug('Impact function is not ready: %s' % prepare_message)
        return {
            'status': prepare_status,
            'message': prepare_message.to_text(),
            'output': {}
        }


@app.task(
    name='inasafe.headless.tasks.run_multi_exposure_analysis',
    queue='inasafe-headless')
def run_multi_exposure_analysis(
        hazard_layer_uri,
        exposure_layer_uris,
        aggregation_layer_uri=None,
        crs=None
):
    """Run analysis for multi exposure.

    :param hazard_layer_uri: Uri to hazard layer.
    :type hazard_layer_uri: basestring

    :param exposure_layer_uris: List of uri to exposure layers.
    :type exposure_layer_uris: list

    :param aggregation_layer_uri: Uri to aggregation layer.
    :type aggregation_layer_uri: basestring

    :param crs: CRS for the analysis (if the aggregation is not set).
    :param crs: QgsCoordinateReferenceSystem

    :returns: A dictionary of output's layer key and Uri with status and
        message.
    :rtype: dict

    The output format will be:
    output = {
        'status': 0,
        'message': '',
        'outputs': {
            'exposure_1': {
                'output_layer_key_11': 'output_layer_path_11',
                'output_layer_key_12': 'output_layer_path_12',
            },
            'exposure_2': {
                'output_layer_key_21': 'output_layer_path_21',
                'output_layer_key_22': 'output_layer_path_22',
            },
            'multi_exposure_output_layer_key_1':
                'multi_exposure_output_layer_path_1',
            'multi_exposure_output_layer_key_2':
                'multi_exposure_output_layer_path_2',
        }
    }
    """
    multi_exposure_if = MultiExposureImpactFunction()
    multi_exposure_if.hazard = load_layer(hazard_layer_uri)[0]
    exposures = [load_layer(layer_uri)[0] for layer_uri in exposure_layer_uris]
    multi_exposure_if.exposures = exposures
    if aggregation_layer_uri:
        multi_exposure_if.aggregation = load_layer(aggregation_layer_uri)[0]
    elif crs:
        multi_exposure_if.crs = crs
    else:
        multi_exposure_if.crs = QgsCoordinateReferenceSystem(4326)
    prepare_status, prepare_message = multi_exposure_if.prepare()
    if prepare_status == PREPARE_SUCCESS:
        LOGGER.debug('Multi exposure function is ready')
        status, message, exposure = multi_exposure_if.run()
        if status == ANALYSIS_SUCCESS:
            outputs = multi_exposure_if.outputs
            output_dict = {}
            # All impact functions
            impact_functions = multi_exposure_if.impact_functions
            for impact_function in impact_functions:
                per_exposure_output = {}
                output = impact_function.outputs
                for layer in output:
                    per_exposure_output[
                        layer.keywords['layer_purpose']] = layer.source()
                output_dict[impact_function.exposure.keywords[
                    'exposure']] = per_exposure_output

            # Multi exposure outputs
            for layer in outputs:
                output_dict[layer.keywords['layer_purpose']] = layer.source()

            # We need to create the multi exposure group because we need
            # the map reports to be generated.
            root = QgsProject.instance().layerTreeRoot()

            group_analysis = root.insertGroup(0, multi_exposure_if.name)
            group_analysis.setVisible(True)
            group_analysis.setCustomProperty(
                MULTI_EXPOSURE_ANALYSIS_FLAG, True)

            for layer in multi_exposure_if.outputs:
                QgsMapLayerRegistry.instance().addMapLayer(layer, False)
                layer_node = group_analysis.addLayer(layer)
                layer_node.setVisible(False)

                # set layer title if any
                try:
                    title = layer.keywords['title']
                    layer.setName(title)
                except KeyError:
                    pass

            for analysis in multi_exposure_if.impact_functions:
                detailed_group = group_analysis.insertGroup(0, analysis.name)
                detailed_group.setVisible(True)
                add_impact_layers_to_canvas(analysis, group=detailed_group)

            return {
                'status': ANALYSIS_SUCCESS,
                'message': '',
                'output': output_dict
            }
        else:
            LOGGER.debug('Analysis failed %s' % message)
            return {
                'status': status,
                'message': message.to_text(),
                'output': {}
            }
    else:
        LOGGER.debug('Impact function is not ready: %s' % prepare_message)
        return {
            'status': prepare_status,
            'message': prepare_message.to_text(),
            'output': {}
        }


@app.task(
    name='inasafe.headless.tasks.generate_report', queue='inasafe-headless')
def generate_report(
        impact_layer_uri,
        custom_report_template_uri=None,
        custom_layer_order=None,
        custom_legend_layer=None):
    """Generate report based on impact layer uri.

    :param impact_layer_uri: The uri to impact layer (one of them).
    :type impact_layer_uri: basestring

    :param custom_report_template_uri: The uri to report template.
    :type custom_report_template_uri: basestring

    :param custom_layer_order: List of layers uri for map report layers order.
    :type custom_layer_order: list

    :returns: A dictionary of output's report key and Uri with status and
        message.
    :rtype: dict

    The output format will be:
    output = {
        'status': 0,
        'message': '',
        'output': {
            'html_product_tag': {
                'action-checklist-report': u'path',
                'analysis-provenance-details-report': u'path',
                'impact-report': u'path',
            },
            'pdf_product_tag': {
                'action-checklist-pdf': u'path',
                'analysis-provenance-details-report-pdf': u'path',
                'impact-report-pdf': u'path',
                'inasafe-map-report-landscape': u'path',
                'inasafe-map-report-portrait': u'path',
            },
            'qpt_product_tag': {
                'inasafe-map-report-landscape': u'path',
                'inasafe-map-report-portrait': u'path',
            }
        },
    }

    """
    output_metadata = read_iso19115_metadata(impact_layer_uri)
    provenances = output_metadata.get('provenance_data', {})
    extra_keywords = output_metadata.get('extra_keywords', {})
    is_multi_exposure = (
        extra_keywords.get(extra_keyword_analysis_type['key']) == (
            MULTI_EXPOSURE_ANALYSIS_FLAG))

    if provenances and is_multi_exposure:
        impact_function = (
            MultiExposureImpactFunction.load_from_output_metadata(
                output_metadata))
    else:
        impact_function = (
            ImpactFunction.load_from_output_metadata(output_metadata))

    IFACE.setActiveLayer(impact_function.analysis_impacted)
    IFACE.zoomToActiveLayer()

    if provenances:
        set_provenance_to_project_variables(provenances)

    generated_components = deepcopy(all_default_report_components)

    if custom_report_template_uri:
        generated_components.remove(map_report)
        generated_components.append(
            override_component_template(
                map_report, custom_report_template_uri))

    error_code, message = (
        impact_function.generate_report(
            generated_components,
            iface=IFACE,
            ordered_layers_uri=custom_layer_order,
            legend_layers_uri=custom_legend_layer))
    return {
        'status': error_code,
        'message': message.to_text(),
        'output': report_urls(impact_function)
    }


@app.task(
    name='inasafe.headless.tasks.get_generated_report',
    queue='inasafe-headless')
def get_generated_report(impact_layer_uri):
    """Get generated report for impact layer uri

    :param impact_layer_uri: The uri to impact layer (one of them).
    :type impact_layer_uri: basestring

    :returns: A dictionary of output's report key and Uri with status and
        message.
    :rtype: dict

    The output format will be:
    output = {
        'status': 0,
        'message': '',
        'output': {
            'html_product_tag': {
                'action-checklist-report': u'path',
                'analysis-provenance-details-report': u'path',
                'impact-report': u'path',
            },
            'pdf_product_tag': {
                'action-checklist-pdf': u'path',
                'analysis-provenance-details-report-pdf': u'path',
                'impact-report-pdf': u'path',
                'inasafe-map-report-landscape': u'path',
                'inasafe-map-report-portrait': u'path',
            },
            'qpt_product_tag': {
                'inasafe-map-report-landscape': u'path',
                'inasafe-map-report-portrait': u'path',
            }
        },
    }

    """
    impact_layer_directory = os.path.split(impact_layer_uri)[0]
    report_metadata_path = os.path.join(
        impact_layer_directory, 'output', 'report_metadata.json')
    try:
        report_metadata = json.load(open(report_metadata_path))
    except IOError:
        return {
            'status': REPORT_METADATA_NOT_EXIST,
            'message': 'Report metadata is not found.',
            'output': {}
        }

    return {
        'status': REPORT_METADATA_EXIST,
        'message': '',
        'output': report_metadata
    }


@app.task(
    name='inasafe.headless.tasks.generate_contour', queue='inasafe-headless')
def generate_contour(layer_uri):
    """Create contour from raster layer_uri to output_uri

    :param layer_uri: The shakemap raster layer uri.
    :type layer_uri: basestring

    :returns: The output layer uri if success
    :rtype: basestring

    It will put the contour layer to
    contour_[input_file_name]_[current_datetime]/[input_file_name].shp

    current_datetime format: 25January2018_09h25-17.597909
    """
    # Always create directory
    input_file_name = os.path.basename(layer_uri)
    input_base_name = os.path.splitext(input_file_name)[0]
    # Make it same format as analysis directory
    current_datetime = datetime.now().strftime('%d%B%Y_%Hh%M-%S.%f')
    output_directory = 'contour_%s_%s' % (input_base_name, current_datetime)
    output_file_name = input_base_name + '.shp'
    output_directory_path = os.path.join(
        setting('defaultUserDirectory'), output_directory)
    # Make sure the output directory exists
    try:
        os.makedirs(output_directory_path)
    except OSError:
        if not os.path.isdir(output_directory_path):
            raise
    output_uri = os.path.join(output_directory_path, output_file_name)

    shakemap_raster = load_layer(layer_uri)[0]
    contour_uri = create_smooth_contour(
        shakemap_raster, output_file_path=output_uri)
    if os.path.exists(contour_uri):
        return contour_uri
    else:
        return None


@app.task(
    name='inasafe.headless.tasks.check_broker_connection',
    queue='inasafe-headless')
def check_broker_connection():
    """Only returns true if broker is connected

    :return: True
    """
    LOGGER.info('proxy tasks')
    return True
