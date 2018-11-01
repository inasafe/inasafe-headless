# coding=utf-8
"""Task for InaSAFE Headless."""

from headless.celery_app import app, start_inasafe
from headless.tasks import inasafe_analysis
from headless.utils import get_headless_logger

__copyright__ = "Copyright 2018, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'

LOGGER = get_headless_logger()


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
    # Initialize QGIS and InaSAFE
    start_inasafe()

    reload(inasafe_analysis)
    metadata = inasafe_analysis.get_keywords(layer_uri, keyword)
    return metadata


@app.task(
    name='inasafe.headless.tasks.run_analysis', queue='inasafe-headless',
    autoretry_for=(Exception,))
def run_analysis(
        hazard_layer_uri,
        exposure_layer_uri,
        aggregation_layer_uri=None,
        crs=None,
        locale='en_US'
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
    # Initialize QGIS and InaSAFE
    start_inasafe(locale)

    reload(inasafe_analysis)
    retval = inasafe_analysis.inasafe_analysis(
        hazard_layer_uri, exposure_layer_uri, aggregation_layer_uri, crs)

    return retval


@app.task(
    name='inasafe.headless.tasks.run_multi_exposure_analysis',
    queue='inasafe-headless',
    autoretry_for=(Exception,))
def run_multi_exposure_analysis(
        hazard_layer_uri,
        exposure_layer_uris,
        aggregation_layer_uri=None,
        crs=None,
        locale='en_US'
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
    # Initialize QGIS and InaSAFE
    start_inasafe(locale)

    reload(inasafe_analysis)
    retval = inasafe_analysis.inasafe_multi_exposure_analysis(
        hazard_layer_uri, exposure_layer_uris, aggregation_layer_uri, crs)

    return retval


@app.task(
    name='inasafe.headless.tasks.generate_report', queue='inasafe-headless',
    autoretry_for=(Exception,))
def generate_report(
        impact_layer_uri,
        custom_report_template_uri=None,
        custom_layer_order=None,
        custom_legend_layer=None,
        use_template_extent=False,
        locale='en_US'):
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
    # Initialize QGIS and InaSAFE
    _, IFACE = start_inasafe(locale)

    reload(inasafe_analysis)
    retval = inasafe_analysis.generate_report(
        impact_layer_uri,
        custom_report_template_uri,
        custom_layer_order,
        custom_legend_layer,
        use_template_extent,
        IFACE)

    return retval


@app.task(
    name='inasafe.headless.tasks.get_generated_report',
    queue='inasafe-headless',
    autoretry_for=(Exception,))
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
    # Initialize QGIS and InaSAFE
    start_inasafe()

    reload(inasafe_analysis)
    result = inasafe_analysis.get_generated_report(impact_layer_uri)
    return result


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
    # Initialize QGIS and InaSAFE
    start_inasafe()

    reload(inasafe_analysis)
    result = inasafe_analysis.generate_contour(layer_uri)
    return result


@app.task(
    name='inasafe.headless.tasks.check_broker_connection',
    queue='inasafe-headless')
def check_broker_connection():
    """Only returns true if broker is connected

    :return: True
    """
    return True


@app.task(
    name='inasafe.headless.tasks.push_to_geonode',
    queue='inasafe-headless-geonode')
def push_to_geonode(layer_uri):
    """Upload layer to geonode instance.

    :param layer_uri: The uri to the layer.
    :type layer_uri: basestring

    :returns: A dictionary of the url of the successfully uploaded layer.
    :rtype: dict

    The output format will be:
    output = {
        'status': 0,
        'message': '',
        'output': {
            'uri': '/layer/layer_name',
            'full_uri': 'http://realtimegeonode.com/layer/layer_name'
        },
    }
    """
    # Initialize QGIS and InaSAFE
    start_inasafe()

    reload(inasafe_analysis)
    result = inasafe_analysis.push_to_geonode(layer_uri)
    return result
