# coding=utf-8
"""Sample file configuration for celery_app worker

This file is intended only for a sample.
Please copy it as celeryconfig.py so it can be read
"""
import os
from distutils.util import strtobool

__author__ = 'Rizky Maulana Nugraha <lana.pcfre@gmail.com>'
__date__ = '1/28/16'


# This is a default value
broker_url = os.environ.get('INASAFE_HEADLESS_broker_host')

result_backend = broker_url

task_routes = {
    'headless.tasks.inasafe_wrapper.run_analysis': {
        'queue': 'inasafe-headless-analysis'
    },

    'headless.tasks.inasafe_wrapper.read_keywords_iso_metadata': {
        'queue': 'inasafe-headless'
    }
}

# RMN: This is really important.

# Long bug description ahead! Beware.

# This set InaSAFE Headless concurrency to 1. Which means this celery worker
# will only uses 1 thread. This is necessary because we are using Xvfb to
# handle graphical report generation (used by processing framework).
# Somehow, qgis processing framework is not thread safe. It forgot to call
# XInitThreads() which is necessary for multithreading. Read long description
# here about XInitThreads(): http://www.remlab.net/op/xlib.shtml
# In other words, you should always set this to 1. If not, it will default to
# number of CPUs/core which can be multithreaded and will invoke debugging
# **NIGHTMARE** to your celery worker. Read about this particular settings
# here:
# http://docs.celeryproject.org/en/latest/configuration.html#celeryd-concurrency
worker_concurrency = 1
worker_prefetch_multiplier = 1

# Celery config
task_serializer = 'pickle'
accept_content = {'pickle'}
result_serializer = 'pickle'

task_always_eager = strtobool(os.environ.get('task_always_eager', 'False'))

DEPLOY_OUTPUT_DIR = os.environ.get('INASAFE_HEADLESS_DEPLOY_OUTPUT_DIR')
DEPLOY_OUTPUT_URL = os.environ.get('INASAFE_HEADLESS_DEPLOY_OUTPUT_URL')
