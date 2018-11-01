# coding=utf-8
import unittest

from headless.settings import PUSH_TO_REALTIME_GEONODE
from headless.tasks.inasafe_analysis import (
    GEONODE_UPLOAD_SUCCESS,
    GEONODE_UPLOAD_FAILED,
)
from headless.tasks.inasafe_wrapper import (
    push_to_geonode,
)
from headless.tasks.test.helpers import geonode_disabled_message, \
    shapefile_layer_uri, tif_layer_uri, ascii_layer_uri, geojson_layer_uri, \
    shakemap_layer_uri, retry_on_worker_lost_error
from safe.test.utilities import get_qgis_app

QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()

__copyright__ = "Copyright 2018, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


class TestGeoNodePush(unittest.TestCase):

    @unittest.skipUnless(PUSH_TO_REALTIME_GEONODE, geonode_disabled_message)
    @retry_on_worker_lost_error()
    def test_push_shapefile_to_geonode(self):
        """Test push shapefile layer to geonode functionality."""
        async_result = push_to_geonode.delay(shapefile_layer_uri)
        result = async_result.get()
        self.assertEqual(
            result['status'], GEONODE_UPLOAD_SUCCESS, result['message'])

    @unittest.skipUnless(PUSH_TO_REALTIME_GEONODE, geonode_disabled_message)
    @retry_on_worker_lost_error()
    def test_push_tif_to_geonode(self):
        """Test push tif layer to geonode functionality."""
        async_result = push_to_geonode.delay(tif_layer_uri)
        result = async_result.get()
        self.assertEqual(
            result['status'], GEONODE_UPLOAD_SUCCESS, result['message'])

    @unittest.skipUnless(PUSH_TO_REALTIME_GEONODE, geonode_disabled_message)
    @retry_on_worker_lost_error()
    def test_push_ascii_to_geonode(self):
        """Test push ascii layer to geonode functionality."""
        async_result = push_to_geonode.delay(ascii_layer_uri)
        result = async_result.get()
        self.assertEqual(
            result['status'], GEONODE_UPLOAD_SUCCESS, result['message'])

    @unittest.skipUnless(PUSH_TO_REALTIME_GEONODE, geonode_disabled_message)
    @retry_on_worker_lost_error()
    def test_push_geojson_to_geonode(self):
        """Test push geojson layer to geonode functionality."""
        async_result = push_to_geonode.delay(geojson_layer_uri)
        result = async_result.get()
        self.assertEqual(
            result['status'], GEONODE_UPLOAD_SUCCESS, result['message'])

    @unittest.skipUnless(PUSH_TO_REALTIME_GEONODE, geonode_disabled_message)
    @retry_on_worker_lost_error()
    def test_push_to_geonode_failed(self):
        """Test push to geonode functionality."""
        async_result = push_to_geonode.delay(
            shakemap_layer_uri,
            geonode_user='NotUser',
            geonode_password='NotPassword')
        result = async_result.get()
        self.assertEqual(result['status'], GEONODE_UPLOAD_FAILED)
        self.assertTrue('Failed to login' in result['message'])
