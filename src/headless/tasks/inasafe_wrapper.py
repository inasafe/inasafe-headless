# coding=utf-8
import logging

from headless.celery_app import app
from qgis.core import QgsCoordinateReferenceSystem
from safe.utilities.metadata import read_iso19115_metadata
from safe.impact_function.impact_function import ImpactFunction
from safe.gis.tools import load_layer
from safe.definitions.constants import PREPARE_SUCCESS, ANALYSIS_SUCCESS

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

    :returns: A dictionary of output's layer key and Uri.
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
