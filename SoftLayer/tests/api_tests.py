"""
    SoftLayer.tests.api_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    :license: MIT, see LICENSE for more details.
"""
import mock

import SoftLayer
import SoftLayer.API
from SoftLayer import consts
from SoftLayer import testing


class Inititialization(testing.TestCase):
    def test_init(self):
        client = SoftLayer.Client(username='doesnotexist',
                                  api_key='issurelywrong', timeout=10)

        self.assertIsInstance(client.auth, SoftLayer.BasicAuthentication)
        self.assertEqual(client.auth.username, 'doesnotexist')
        self.assertEqual(client.auth.api_key, 'issurelywrong')
        self.assertEqual(client.endpoint_url,
                         SoftLayer.API_PUBLIC_ENDPOINT.rstrip('/'))
        self.assertEqual(client.timeout, 10)

    @mock.patch('SoftLayer.config.get_client_settings')
    def test_env(self, get_client_settings):
        auth = mock.Mock()
        get_client_settings.return_value = {
            'auth': auth,
            'timeout': 10,
            'endpoint_url': 'http://endpoint_url/',
        }
        client = SoftLayer.Client()
        self.assertEqual(client.auth.get_headers(), auth.get_headers())
        self.assertEqual(client.timeout, 10)
        self.assertEqual(client.endpoint_url, 'http://endpoint_url')


class ClientMethods(testing.TestCase):
    def test_help(self):
        help(SoftLayer)
        help(SoftLayer.Client)
        client = SoftLayer.Client(
            username='doesnotexist',
            api_key='issurelywrong'
        )
        help(client)
        help(client['SERVICE'])

    def test_repr(self):
        client = SoftLayer.Client(
            username='doesnotexist',
            api_key='issurelywrong'
        )
        self.assertIn("Client", repr(client))

    def test_service_repr(self):
        client = SoftLayer.Client(
            username='doesnotexist',
            api_key='issurelywrong'
        )
        self.assertIn("Service", repr(client['SERVICE']))

    def test_len(self):
        client = SoftLayer.Client(
            username='doesnotexist',
            api_key='issurelywrong'
        )
        self.assertEqual(len(client), 0)


class APIClient(testing.TestCase):
    def set_up(self):
        self.client = SoftLayer.Client(
            username='doesnotexist', api_key='issurelywrong',
            endpoint_url="ENDPOINT")

    @mock.patch('SoftLayer.transports.make_xml_rpc_api_call')
    def test_simple_call(self, make_xml_rpc_api_call):
        self.client['SERVICE'].METHOD()
        make_xml_rpc_api_call.assert_called_with(
            'ENDPOINT/SoftLayer_SERVICE', 'METHOD', (),
            headers={
                'authenticate': {
                    'username': 'doesnotexist', 'apiKey': 'issurelywrong'}},
            proxy=None,
            timeout=None,
            http_headers={
                'Content-Type': 'application/xml',
                'User-Agent': consts.USER_AGENT,
                'Accept': '*/*',
                'Accept-Encoding': 'gzip, deflate, compress',
            })

    @mock.patch('SoftLayer.transports.make_xml_rpc_api_call')
    def test_complex(self, make_xml_rpc_api_call):
        self.client['SERVICE'].METHOD(
            1234,
            id=5678,
            mask={'object': {'attribute': ''}},
            raw_headers={'RAW': 'HEADER'},
            filter={
                'TYPE': {'obj': {'attribute': {'operation': '^= prefix'}}}},
            limit=9, offset=10)

        make_xml_rpc_api_call.assert_called_with(
            'ENDPOINT/SoftLayer_SERVICE', 'METHOD', (1234, ),
            headers={
                'SoftLayer_SERVICEObjectMask': {
                    'mask': {'object': {'attribute': ''}}},
                'SoftLayer_SERVICEObjectFilter': {
                    'TYPE': {
                        'obj': {'attribute': {'operation': '^= prefix'}}}},
                'authenticate': {
                    'username': 'doesnotexist', 'apiKey': 'issurelywrong'},
                'SoftLayer_SERVICEInitParameters': {'id': 5678},
                'resultLimit': {'limit': 9, 'offset': 10}},
            proxy=None,
            timeout=None,
            http_headers={
                'RAW': 'HEADER',
                'Content-Type': 'application/xml',
                'User-Agent': consts.USER_AGENT,
                'Accept': '*/*',
                'Accept-Encoding': 'gzip, deflate, compress',
            })

    @mock.patch('SoftLayer.transports.make_xml_rpc_api_call')
    def test_mask_call_v2(self, make_xml_rpc_api_call):
        self.client['SERVICE'].METHOD(
            mask="mask[something[nested]]")
        make_xml_rpc_api_call.assert_called_with(
            'ENDPOINT/SoftLayer_SERVICE', 'METHOD', (),
            headers={
                'authenticate': {
                    'username': 'doesnotexist', 'apiKey': 'issurelywrong'},
                'SoftLayer_ObjectMask': {'mask': 'mask[something[nested]]'}},
            proxy=None,
            timeout=None,
            http_headers={
                'Content-Type': 'application/xml',
                'User-Agent': consts.USER_AGENT,
                'Accept': '*/*',
                'Accept-Encoding': 'gzip, deflate, compress',
            })

    @mock.patch('SoftLayer.transports.make_xml_rpc_api_call')
    def test_mask_call_v2_dot(self, make_xml_rpc_api_call):
        self.client['SERVICE'].METHOD(
            mask="mask.something.nested")
        make_xml_rpc_api_call.assert_called_with(
            'ENDPOINT/SoftLayer_SERVICE', 'METHOD', (),
            headers={
                'authenticate': {
                    'username': 'doesnotexist', 'apiKey': 'issurelywrong'},
                'SoftLayer_ObjectMask': {'mask': 'mask.something.nested'}},
            proxy=None,
            timeout=None,
            http_headers={
                'Content-Type': 'application/xml',
                'User-Agent': consts.USER_AGENT,
                'Accept': '*/*',
                'Accept-Encoding': 'gzip, deflate, compress',
            })

    @mock.patch('SoftLayer.transports.make_xml_rpc_api_call')
    def test_mask_call_no_mask_prefix(self, make_xml_rpc_api_call):
        self.client['SERVICE'].METHOD(mask="something.nested")
        make_xml_rpc_api_call.assert_called_with(
            'ENDPOINT/SoftLayer_SERVICE', 'METHOD', (),
            headers={
                'authenticate': {
                    'username': 'doesnotexist', 'apiKey': 'issurelywrong'},
                'SoftLayer_ObjectMask': {'mask': 'mask[something.nested]'}},
            proxy=None,
            timeout=None,
            http_headers={
                'Content-Type': 'application/xml',
                'User-Agent': consts.USER_AGENT,
                'Accept': '*/*',
                'Accept-Encoding': 'gzip, deflate, compress',
            })

    @mock.patch('SoftLayer.API.Client.iter_call')
    def test_iterate(self, _iter_call):
        self.client['SERVICE'].METHOD(iter=True)
        _iter_call.assert_called_with('SERVICE', 'METHOD')

    @mock.patch('SoftLayer.API.Client.iter_call')
    def test_service_iter_call(self, _iter_call):
        self.client['SERVICE'].iter_call('METHOD')
        _iter_call.assert_called_with('SERVICE', 'METHOD')

    @mock.patch('SoftLayer.API.Client.call')
    def test_iter_call(self, _call):
        # chunk=100, no limit
        _call.side_effect = [list(range(100)), list(range(100, 125))]
        result = list(self.client.iter_call('SERVICE', 'METHOD', iter=True))

        self.assertEqual(list(range(125)), result)
        _call.assert_has_calls([
            mock.call('SERVICE', 'METHOD', limit=100, iter=False, offset=0),
            mock.call('SERVICE', 'METHOD', limit=100, iter=False, offset=100),
        ])
        _call.reset_mock()

        # chunk=100, no limit. Requires one extra request.
        _call.side_effect = [list(range(100)), list(range(100, 200)), []]
        result = list(self.client.iter_call('SERVICE', 'METHOD', iter=True))
        self.assertEqual(list(range(200)), result)
        _call.assert_has_calls([
            mock.call('SERVICE', 'METHOD', limit=100, iter=False, offset=0),
            mock.call('SERVICE', 'METHOD', limit=100, iter=False, offset=100),
            mock.call('SERVICE', 'METHOD', limit=100, iter=False, offset=200),
        ])
        _call.reset_mock()

        # chunk=25, limit=30
        _call.side_effect = [list(range(0, 25)), list(range(25, 30))]
        result = list(self.client.iter_call(
            'SERVICE', 'METHOD', iter=True, limit=30, chunk=25))
        self.assertEqual(list(range(30)), result)
        _call.assert_has_calls([
            mock.call('SERVICE', 'METHOD', iter=False, limit=25, offset=0),
            mock.call('SERVICE', 'METHOD', iter=False, limit=5, offset=25),
        ])
        _call.reset_mock()

        # A non-list was returned
        _call.side_effect = ["test"]
        result = list(self.client.iter_call('SERVICE', 'METHOD', iter=True))
        self.assertEqual(["test"], result)
        _call.assert_has_calls([
            mock.call('SERVICE', 'METHOD', iter=False, limit=100, offset=0),
        ])
        _call.reset_mock()

        # chunk=25, limit=30, offset=12
        _call.side_effect = [list(range(0, 25)), list(range(25, 30))]
        result = list(self.client.iter_call(
            'SERVICE', 'METHOD', iter=True, limit=30, chunk=25, offset=12))
        self.assertEqual(list(range(30)), result)
        _call.assert_has_calls([
            mock.call('SERVICE', 'METHOD', iter=False, limit=25, offset=12),
            mock.call('SERVICE', 'METHOD', iter=False, limit=5, offset=37),
        ])

        # Chunk size of 0 is invalid
        self.assertRaises(
            AttributeError,
            lambda: list(self.client.iter_call(
                'SERVICE', 'METHOD', iter=True, chunk=0)))

    def test_call_invalid_arguments(self):
        self.assertRaises(
            TypeError,
            self.client.call, 'SERVICE', 'METHOD', invalid_kwarg='invalid')

    @mock.patch('SoftLayer.transports.make_xml_rpc_api_call')
    def test_call_compression_disabled(self, make_xml_rpc_api_call):
        self.client['SERVICE'].METHOD(compress=False)
        make_xml_rpc_api_call.assert_called_with(
            'ENDPOINT/SoftLayer_SERVICE', 'METHOD', (),
            headers=mock.ANY,
            proxy=None,
            timeout=None,
            http_headers={
                'Content-Type': 'application/xml',
                'User-Agent': consts.USER_AGENT,
            })

    @mock.patch('SoftLayer.transports.make_xml_rpc_api_call')
    def test_call_compression_enabled(self, make_xml_rpc_api_call):
        self.client['SERVICE'].METHOD(compress=True)
        make_xml_rpc_api_call.assert_called_with(
            'ENDPOINT/SoftLayer_SERVICE', 'METHOD', (),
            headers=mock.ANY,
            proxy=None,
            timeout=None,
            http_headers={
                'Content-Type': 'application/xml',
                'User-Agent': consts.USER_AGENT,
                'Accept': '*/*',
                'Accept-Encoding': 'gzip, deflate, compress',
            })

    @mock.patch('SoftLayer.transports.make_xml_rpc_api_call')
    def test_call_compression_override(self, make_xml_rpc_api_call):
        # raw_headers should override compress=False
        self.client['SERVICE'].METHOD(
            compress=False,
            raw_headers={'Accept-Encoding': 'gzip'})
        make_xml_rpc_api_call.assert_called_with(
            'ENDPOINT/SoftLayer_SERVICE', 'METHOD', (),
            headers=mock.ANY,
            proxy=None,
            timeout=None,
            http_headers={
                'Content-Type': 'application/xml',
                'User-Agent': consts.USER_AGENT,
                'Accept-Encoding': 'gzip',
            })


class APITimedClient(testing.TestCase):
    def set_up(self):
        self.client = SoftLayer.TimedClient(
            username='doesnotexist', api_key='issurelywrong',
            endpoint_url="ENDPOINT")

    @mock.patch('SoftLayer.API.time.time')
    @mock.patch('SoftLayer.API.Client.call')
    def test_overriden_call_times_methods(self, _call, _time):
        _call.side_effect = [list(range(10))]
        _time.side_effect = [1121362200, 1121762200]

        result = list(self.client.call('SERVICE', 'METHOD'))

        self.assertEqual(list(range(10)), result)

        expected_calls = [('SERVICE.METHOD', 1121362200, 400000)]
        self.assertEqual(expected_calls, self.client.get_last_calls())


class UnauthenticatedAPIClient(testing.TestCase):
    def set_up(self):
        self.client = SoftLayer.Client(endpoint_url="ENDPOINT")

    @mock.patch('SoftLayer.config.get_client_settings')
    def test_init(self, get_client_settings):
        get_client_settings.return_value = {}
        client = SoftLayer.Client()
        self.assertIsNone(client.auth)

    @mock.patch('SoftLayer.config.get_client_settings')
    def test_init_with_proxy(self, get_client_settings):
        get_client_settings.return_value = {'proxy': 'http://localhost:3128'}
        client = SoftLayer.Client()
        self.assertEqual(client.proxy, 'http://localhost:3128')

    @mock.patch('SoftLayer.API.Client.call')
    def test_authenticate_with_password(self, _call):
        _call.return_value = {
            'userId': 12345,
            'hash': 'TOKEN',
        }
        self.client.authenticate_with_password('USERNAME', 'PASSWORD')
        _call.assert_called_with(
            'User_Customer',
            'getPortalLoginToken',
            'USERNAME',
            'PASSWORD',
            None,
            None)
        self.assertIsNotNone(self.client.auth)
        self.assertEqual(self.client.auth.user_id, 12345)
        self.assertEqual(self.client.auth.auth_token, 'TOKEN')
