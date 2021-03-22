"""
    SoftLayer.config
    ~~~~~~~~~~~~~~~~
    Handles different methods for loading configuration for the API bindings

    :license: MIT, see LICENSE for more details.
"""
import configparser
import logging
import os
import os.path

LOGGER = logging.getLogger(__name__)

def get_client_settings_args(**kwargs):
    """Retrieve client settings from user-supplied arguments.

        :param \\*\\*kwargs: Arguments that are passed into the client instance
    """
    timeout = kwargs.get('timeout')
    if timeout is not None:
        timeout = float(timeout)

    return {
        'endpoint_url': kwargs.get('endpoint_url'),
        'timeout': timeout,
        'proxy': kwargs.get('proxy'),
        'username': kwargs.get('username'),
        'api_key': kwargs.get('api_key'),
    }


def get_client_settings_env(**_):
    """Retrieve client settings from environment settings.

        :param \\*\\*kwargs: Arguments that are passed into the client instance
    """

    return {
        'proxy': os.environ.get('https_proxy'),
        'username': os.environ.get('SL_USERNAME'),
        'api_key': os.environ.get('SL_API_KEY'),
    }


def get_client_settings_config_file(**kwargs):  # pylint: disable=inconsistent-return-statements
    """Retrieve client settings from the possible config file locations.

        :param \\*\\*kwargs: Arguments that are passed into the client instance
    """
    config_files = ['/etc/softlayer.conf', '~/.softlayer']
    if kwargs.get('config_file'):
        config_files.append(kwargs.get('config_file'))
    config_files = [os.path.expanduser(f) for f in config_files]
    config = configparser.RawConfigParser({
        'username': '',
        'api_key': '',
        'endpoint_url': '',
        'timeout': '0',
        'proxy': '',
    })
    config.read(config_files)

    if config.has_section('softlayer'):
        return {
            'endpoint_url': config.get('softlayer', 'endpoint_url'),
            'timeout': config.getfloat('softlayer', 'timeout'),
            'proxy': config.get('softlayer', 'proxy'),
            'username': config.get('softlayer', 'username'),
            'api_key': config.get('softlayer', 'api_key'),
        }


SETTING_RESOLVERS = [get_client_settings_args,
                     get_client_settings_env,
                     get_client_settings_config_file]


def get_client_settings(**kwargs):
    """Parse client settings.

    Parses settings from various input methods, preferring earlier values
    to later ones. The settings currently come from explicit user arguments,
    environmental variables and config files.

        :param \\*\\*kwargs: Arguments that are passed into the client instance
    """
    all_settings = {}
    for setting_method in SETTING_RESOLVERS:
        settings = setting_method(**kwargs)
        if settings:
            settings.update((k, v) for k, v in all_settings.items() if v)
            all_settings = settings

    return all_settings


def get_config(config_file=None):
    if config_file is None:
        config_file = '~/.softlayer'
    config = configparser.ConfigParser()
    config.read(os.path.expanduser(config_file))
    return config

def write_config(configuration, config_file=None):
    if config_file is None:
        config_file = '~/.softlayer'
    config_file = os.path.expanduser(config_file)
    LOGGER.warning("Updating config file {} with new access tokens".format(config_file))
    with open(config_file, 'w') as file:
        configuration.write(file)