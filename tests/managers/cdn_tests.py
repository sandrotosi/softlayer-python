"""
    SoftLayer.tests.managers.cdn_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :license: MIT, see LICENSE for more details.
"""

from SoftLayer import fixtures
from SoftLayer.managers import cdn
from SoftLayer import testing


class CDNTests(testing.TestCase):

    def set_up(self):
        self.cdn_client = cdn.CDNManager(self.client)

    def test_list_accounts(self):
        self.cdn_client.list_cdn()
        self.assert_called_with('SoftLayer_Network_CdnMarketplace_Configuration_Mapping',
                                'listDomainMappings')

    def test_detail_cdn(self):
        self.cdn_client.get_cdn("12345")

        args = ("12345",)
        self.assert_called_with('SoftLayer_Network_CdnMarketplace_Configuration_Mapping',
                                'listDomainMappingByUniqueId',
                                args=args)

    def test_detail_usage_metric(self):
        self.cdn_client.get_usage_metrics(12345, history=30, frequency="aggregate")

        args = (12345,
                self.cdn_client.start_data,
                self.cdn_client.end_date,
                "aggregate")
        self.assert_called_with('SoftLayer_Network_CdnMarketplace_Metrics',
                                'getMappingUsageMetrics',
                                args=args)

    def test_get_origins(self):
        self.cdn_client.get_origins("12345")
        self.assert_called_with('SoftLayer_Network_CdnMarketplace_Configuration_Mapping_Path',
                                'listOriginPath')

    def test_add_origin(self):
        self.cdn_client.add_origin("12345", "10.10.10.1", "/example/videos", origin_type="server",
                                   header="test.example.com", port=80, protocol='http', optimize_for="web",
                                   cache_query="include all")

        args = ({
            'uniqueId': "12345",
            'origin': '10.10.10.1',
            'path': '/example/videos',
                    'originType': 'HOST_SERVER',
                    'header': 'test.example.com',
                    'httpPort': 80,
                    'protocol': 'HTTP',
                    'performanceConfiguration': 'General web delivery',
                    'cacheKeyQueryRule': "include all"
        },)
        self.assert_called_with('SoftLayer_Network_CdnMarketplace_Configuration_Mapping_Path',
                                'createOriginPath',
                                args=args)

    def test_add_origin_with_bucket_and_file_extension(self):
        self.cdn_client.add_origin("12345", "10.10.10.1", "/example/videos", origin_type="storage",
                                   bucket_name="test-bucket", file_extensions="jpg", header="test.example.com", port=80,
                                   protocol='http', optimize_for="web", cache_query="include all")

        args = ({
            'uniqueId': "12345",
            'origin': '10.10.10.1',
            'path': '/example/videos',
                    'originType': 'OBJECT_STORAGE',
                    'header': 'test.example.com',
                    'httpPort': 80,
                    'protocol': 'HTTP',
                    'bucketName': 'test-bucket',
                    'fileExtension': 'jpg',
                    'performanceConfiguration': 'General web delivery',
                    'cacheKeyQueryRule': "include all"
        },)
        self.assert_called_with('SoftLayer_Network_CdnMarketplace_Configuration_Mapping_Path',
                                'createOriginPath',
                                args=args)

    def test_remove_origin(self):
        self.cdn_client.remove_origin("12345", "/example1")

        args = ("12345",
                "/example1")
        self.assert_called_with('SoftLayer_Network_CdnMarketplace_Configuration_Mapping_Path',
                                'deleteOriginPath',
                                args=args)

    def test_purge_content(self):
        self.cdn_client.purge_content("12345", "/example1")

        args = ("12345",
                "/example1")
        self.assert_called_with('SoftLayer_Network_CdnMarketplace_Configuration_Cache_Purge',
                                'createPurge',
                                args=args)

    def test_cdn_edit(self):
        identifier = '9934111111111'
        header = 'www.test.com'
        result = self.cdn_client.edit(identifier, header=header)

        self.assertEqual(fixtures.SoftLayer_Network_CdnMarketplace_Configuration_Mapping.
                         updateDomainMapping, result)

        self.assert_called_with(
            'SoftLayer_Network_CdnMarketplace_Configuration_Mapping',
            'updateDomainMapping',
            args=({
                'uniqueId': '9934111111111',
                'originType': 'HOST_SERVER',
                'protocol': 'HTTP',
                'path': '/',
                'vendorName': 'akamai',
                'cname': 'cdnakauuiet7s6u6.cdnedge.bluemix.net',
                'domain': 'test.example.com',
                'httpPort': 80,
                'header': 'www.test.com',
                'origin': '1.1.1.1'
            },)
        )

    def test_cdn_instance_by_hostname(self):
        hostname = 'test.example.com'
        result = self.cdn_client._get_ids_from_hostname(hostname)
        expected_result = fixtures.SoftLayer_Network_CdnMarketplace_Configuration_Mapping.listDomainMappings
        self.assertEqual(expected_result[0]['uniqueId'], result[0])
        self.assert_called_with(
            'SoftLayer_Network_CdnMarketplace_Configuration_Mapping',
            'listDomainMappings',)
