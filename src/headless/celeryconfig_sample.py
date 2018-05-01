# coding=utf-8
"""Sample file configuration for celery_app worker

This file is intended only for a sample.
Please copy it as celeryconfig.py so it can be read
"""
import os
import ast

__copyright__ = "Copyright 2018, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


# This is a default value
broker_url = os.environ.get('INASAFE_HEADLESS_BROKER_HOST')

result_backend = broker_url


task_routes = {
    'inasafe.headless.tasks.get_keywords': {
        'queue': 'inasafe-headless'
    },
    'inasafe.headless.tasks.run_analysis': {
        'queue': 'inasafe-headless-analysis'
    },
    'inasafe.headless.tasks.run_multi_exposure_analysis': {
        'queue': 'inasafe-headless-analysis'
    },
    'inasafe.headless.tasks.generate_report': {
        'queue': 'inasafe-headless-reporting'
    },
    'inasafe.headless.tasks.get_generated_report': {
        'queue': 'inasafe-headless'
    },
    'inasafe.headless.tasks.generate_contour': {
        'queue': 'inasafe-headless-contour'
    },
    'inasafe.headless.tasks.check_broker_connection': {
        'queue': 'inasafe-headless'
    },
    'inasafe.headless.tasks.push_to_geonode': {
        'queue': 'inasafe-headless-geonode'
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


# Late ACK settings
task_acks_late = True
task_reject_on_worker_lost = True


task_always_eager = ast.literal_eval(
    os.environ.get('TASK_ALWAYS_EAGER', 'False'))
