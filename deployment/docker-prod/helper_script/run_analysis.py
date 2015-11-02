#!/usr/bin/env python
# coding=utf-8
import glob
import sys
import shutil
import os
from safe.engine.core import calculate_impact
from safe.impact_functions import register_impact_functions
from safe.impact_functions.impact_function_manager import \
    ImpactFunctionManager
from safe.storage.core import read_layer
from safe.storage.safe_layer import SafeLayer
from safe.storage.utilities import safe_to_qgis_layer
from safe.utilities.styling import set_vector_categorized_style, \
    set_vector_graduated_style, setRasterStyle

__author__ = 'lucernae'
__email__ = 'lana.pcfre@gmail.com'

# This script will be executed from inasafe folder


class AnalysisArguments(object):
    """
    Provides shortcut method to get analysis arguments from command line
    """

    def __init__(self):
        self.hazard_filename = None
        self.exposure_filename = None
        self.aggregation_filename = None
        self.impact_filename = None
        self.impact_function_name = None

    @classmethod
    def read_arguments(cls):
        """

        :return:
        """
        arg = AnalysisArguments()

        arg.hazard_filename = os.environ.get('HAZARD')
        arg.exposure_filename = os.environ.get('EXPOSURE')
        arg.aggregation_filename = os.environ.get('AGGREGATION')
        arg.impact_function_name = os.environ.get('FUNCTION')
        arg.impact_filename = os.environ.get('IMPACT')

        if not (arg.hazard_filename and arg.exposure_filename and
                    arg.impact_function_name and arg.impact_filename):
            print "How to use: "
            print "Available environment args:"
            print "HAZARD : hazard filename"
            print "EXPOSURE : exposure filename"
            print "AGGREGATION : aggregation filename"
            print "IMPACT : impact filename"
            print "FUNCTION : impact function name"

            return None

        return arg


def copy_impact_layer(impact, impact_filename):
    result_filename, extension = os.path.splitext(impact.filename)
    for f in glob.glob('%s.*' % result_filename):
        print 'Copying file %s' % f
        target_filename = f.replace(result_filename, impact_filename)
        shutil.copyfile(f, target_filename)
    impact_fullname = '%s%s' % (impact_filename, extension)
    print 'Impact file %s created.' % impact_fullname


def generate_styles(safe_impact_layer, qgis_impact_layer):
    # Get requested style for impact layer of either kind
    style = safe_impact_layer.get_style_info()
    style_type = safe_impact_layer.get_style_type()

    # Determine styling for QGIS layer
    if safe_impact_layer.is_vector:
        if not style:
            # Set default style if possible
            pass
        elif style_type == 'categorizedSymbol':
            set_vector_categorized_style(qgis_impact_layer, style)
        elif style_type == 'graduatedSymbol':
            set_vector_graduated_style(qgis_impact_layer, style)

    elif safe_impact_layer.is_raster:
        if not style:
            qgis_impact_layer.setDrawingStyle("SingleBandPseudoColor")
        else:
            setRasterStyle(qgis_impact_layer, style)


def direct_execution():

    arg = AnalysisArguments.read_arguments()

    register_impact_functions()

    registry = ImpactFunctionManager().registry

    function = registry.get_instance(arg.impact_function_name)
    function.hazard = SafeLayer(read_layer(arg.hazard_filename))
    function.exposure = SafeLayer(read_layer(arg.exposure_filename))

    impact = calculate_impact(function)
    qgis_impact = safe_to_qgis_layer(impact)

    generate_styles(impact, qgis_impact)

    copy_impact_layer(impact, arg.impact_filename)


def analysis_execution():

    from safe.test.utilities import get_qgis_app

    # get_qgis_app must be called before importing Analysis
    QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()

    from safe.utilities.analysis import Analysis
    from safe.utilities.keyword_io import KeywordIO

    analysis = Analysis()

    arg = AnalysisArguments.read_arguments()

    register_impact_functions()

    registry = ImpactFunctionManager().registry

    function = registry.get_instance(arg.impact_function_name)

    hazard_layer = safe_to_qgis_layer(read_layer(arg.hazard_filename))
    exposure_layer = safe_to_qgis_layer(read_layer(arg.exposure_filename))
    if arg.aggregation_filename:
        aggregation_layer = safe_to_qgis_layer(read_layer(
            arg.aggregation_filename))

    keywords_io = KeywordIO()

    try:
        analysis.map_canvas = IFACE.mapCanvas()
        analysis.hazard_layer = hazard_layer
        analysis.hazard_keyword = keywords_io.read_keywords(hazard_layer)
        analysis.exposure_layer = exposure_layer
        analysis.exposure_keyword = keywords_io.read_keywords(exposure_layer)
        if aggregation_layer:
            print 'Using aggregation layer'
            analysis.aggregation_layer = aggregation_layer
            analysis.aggregation_keyword = keywords_io.read_keywords(
                aggregation_layer)
        analysis.impact_function = function

        analysis.setup_analysis()
        print 'Setup analysis done'
        analysis.run_analysis()
        print 'Analysis done'
    except Exception as e:
        print e.message

    impact = analysis.impact_layer
    qgis_impact = safe_to_qgis_layer(impact)

    generate_styles(impact, qgis_impact)

    copy_impact_layer(impact, arg.impact_filename)

if __name__ == '__main__':
    analysis_execution()
