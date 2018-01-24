# coding=utf-8
"""Task for InaSAFE Headless."""
import logging
import os

from headless.celery_app import app
from qgis.core import QgsCoordinateReferenceSystem
from safe.utilities.metadata import read_iso19115_metadata
from safe.impact_function.impact_function import ImpactFunction
from safe.impact_function.multi_exposure_wrapper import (
    MultiExposureImpactFunction)
from safe.gis.tools import load_layer
from safe.gis.raster.contour import create_smooth_contour
from safe.definitions.constants import PREPARE_SUCCESS, ANALYSIS_SUCCESS

__copyright__ = "Copyright 2018, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'

LOGGER = logging.getLogger('InaSAFE')


@app.task(queue='inasafe-headless')
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
    return read_iso19115_metadata(layer_uri, keyword)


@app.task(queue='inasafe-headless')
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

            return {
                'status': ANALYSIS_SUCCESS,
                'message': '',
                'output': output_dict
            }
        else:
            LOGGER.debug('Analysis failed %s' % message)
            return {
                'status': status,
                'message': message,
                'output': {}
            }
    else:
        LOGGER.debug('Impact function is not ready: %s' % prepare_message)
        return {
            'status': prepare_status,
            'message': prepare_message,
            'output': {}
        }


@app.task(queue='inasafe-headless')
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
        status, message = multi_exposure_if.run()
        if status == ANALYSIS_SUCCESS:
            outputs = multi_exposure_if.outputs
            output_dict = {}
            for layer in outputs:
                output_dict[layer.keywords['layer_purpose']] = layer.source()

            return {
                'status': ANALYSIS_SUCCESS,
                'message': '',
                'output': output_dict
            }
        else:
            LOGGER.debug('Analysis failed %s' % message)
            return {
                'status': status,
                'message': message,
                'output': {}
            }
    else:
        LOGGER.debug('Impact function is not ready: %s' % prepare_message)
        return {
            'status': prepare_status,
            'message': prepare_message,
            'output': {}
        }


@app.task(queue='inasafe-headless')
def generate_report():
    pass


@app.task(queue='inasafe-headless')
def generate_contour(layer_uri, output_uri=None):
    """Create contour from raster layer_uri to output_uri

    :param layer_uri: The shakemap raster layer uri.
    :type layer_uri: basestring

    :param output_uri: The contour output layer uri
    :type output_uri: basestring

    :returns: The output layer uri if success
    :rtype: basestring
    """
    shakemap_raster = load_layer(layer_uri)[0]
    contour_uri = create_smooth_contour(
        shakemap_raster, output_file_path=output_uri)
    if os.path.exists(contour_uri):
        return contour_uri
    else:
        return None
