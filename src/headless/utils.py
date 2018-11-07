# coding=utf-8
import logging
import os

from qgis.core import QgsMapLayer

from headless import settings as headless_settings
from safe.common.exceptions import NoKeywordsFoundError
from safe.gis.tools import load_layer as inasafe_load_layer
from safe.utilities.keyword_io import KeywordIO
from safe.utilities.metadata import read_iso19115_metadata
from safe.utilities.utilities import monkey_patch_keywords


def set_logger():
    """Set default log level"""
    # Initialize logger
    logger = logging.getLogger('InaSAFE')
    logger.setLevel(headless_settings.INASAFE_LOG_LEVEL)


def get_headless_logger():
    """Get an instance of InaSAFE Headless logger."""
    logger = logging.getLogger('InaSAFE Headless')
    logger.setLevel(headless_settings.HEADLESS_LOG_LEVEL)
    return logger


def load_layer(full_layer_uri_string, name=None, provider=None):
    """Helper method to override InaSAFE load layer method.

    This method will specifically handle QLR definitions.

    :param provider: The provider name to use if known to open the layer.
        Default to None, we will try to guess it, but it's much better if you
        can provide it.
    :type provider:

    :param name: The name of the layer. If not provided, it will be computed
        based on the URI.
    :type name: basestring

    :param full_layer_uri_string: Layer URI, with provider type.
    :type full_layer_uri_string: str

    :returns: tuple containing layer and its layer_purpose.
    :rtype: (QgsMapLayer, str)
    """
    # If it ends with QLR extensions, most probably it is a QLR file
    base, ext = os.path.splitext(full_layer_uri_string)

    if ext.lower() == '.qlr':
        layer = QgsMapLayer.fromLayerDefinitionFile(full_layer_uri_string)
        if not layer:
            return None, None

        layer = layer[0]
        if layer.isValid():
            keyword_io = KeywordIO()

            try:
                # layer keywords read probably fails if it is a remote data
                # source. Attempt to search for local xml file first
                keywords = read_iso19115_metadata(full_layer_uri_string)
                layer.keywords = keywords

                # if succeed, remember the keyword in QGIS Metadata for
                # current process cache
                keyword_io.write_keywords(layer, keywords)
            except NoKeywordsFoundError:
                # if previous attempt fails

                # update the layer keywords
                monkey_patch_keywords(layer)

            layer_purpose = layer.keywords.get('layer_purpose')

            return layer, layer_purpose

    # Deal with other cases
    return inasafe_load_layer(
        full_layer_uri_string, name=name, provider=provider)
