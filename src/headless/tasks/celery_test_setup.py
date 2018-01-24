# coding=utf-8
"""Celery test set up."""

import logging
import os
import ast

__copyright__ = "Copyright 2018, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


LOGGER = logging.getLogger('InaSAFE')
LOGGER.setLevel(logging.DEBUG)


def update_celery_configuration(app):
    """Update celery app configuration for test purposes

    Useful to toggle between eager test and async test

    :param app: App configuration
    :type app: celery.Celery
    :return:
    """
    celery_always_eager = ast.literal_eval(os.environ.get(
        'CELERY_ALWAYS_EAGER', 'False'))
    app.conf.update(
        CELERY_ALWAYS_EAGER=celery_always_eager
    )
