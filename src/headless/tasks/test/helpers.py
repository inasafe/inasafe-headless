# coding=utf-8
import os
from functools import wraps

from billiard.exceptions import WorkerLostError

from headless.utils import get_headless_logger
from safe.test.utilities import standard_data_path

dir_path = os.path.dirname(os.path.realpath(__file__))

# Layers
earthquake_layer_uri = os.path.join(
    dir_path, 'data', 'input_layers', 'earthquake.asc')
shakemap_layer_uri = os.path.join(
    dir_path, 'data', 'input_layers', 'grid-use_ascii.tif')
place_layer_uri = os.path.join(
    dir_path, 'data', 'input_layers', 'places.geojson')
aggregation_layer_uri = os.path.join(
    dir_path, 'data', 'input_layers', 'small_grid.geojson')
population_multi_fields_layer_uri = os.path.join(
    dir_path, 'data', 'input_layers', 'population_multi_fields.geojson')
buildings_layer_uri = os.path.join(
    dir_path, 'data', 'input_layers', 'buildings.geojson')
buildings_layer_qlr_uri = os.path.join(
    dir_path, 'data', 'input_layers', 'buildings.qlr')

shapefile_layer_uri = standard_data_path('exposure', 'airports.shp')
ascii_layer_uri = standard_data_path('gisv4', 'hazard', 'earthquake.asc')
tif_layer_uri = standard_data_path('hazard', 'earthquake.tif')
geojson_layer_uri = standard_data_path(
    'gisv4', 'hazard', 'classified_vector.geojson')

# Map template
custom_map_template_basename = 'custom-inasafe-map-report-landscape'
custom_map_template = os.path.join(
    dir_path, 'data', custom_map_template_basename + '.qpt'
)

settings_path = os.path.join(
    dir_path, 'data/settings/custom_setting.json'
)

minimum_needs_mapping_path = os.path.join(
    dir_path, 'data/settings/custom_locale_minimum_needs_mapping.json'
)


# Common message
geonode_disabled_message = (
    'Only run this test if we set the PUSH_TO_REALTIME_GEONODE variable to '
    'True.')

LOGGER = get_headless_logger()


def retry_on_worker_lost_error(times=5):
    """Retry test method if failed because WorkerLostError.

    :param times: Number of tries
    :type times: int
    """
    def _decorator(func):

        @wraps(func)
        def wrapper(*args, **kwargs):
            for i in range(times):
                try:
                    return func(*args, **kwargs)
                except WorkerLostError as e:
                    LOGGER.info(
                        'function {} failed '
                        'because WorkerLostError'.format(func))
                    LOGGER.info(e)
        return wrapper
    return _decorator
