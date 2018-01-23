# coding=utf-8
import logging

from headless.celery_app import app
from safe.utilities.metadata import read_iso19115_metadata

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
