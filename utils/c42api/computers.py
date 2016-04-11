"""
A module for fetching every device on a Code42 installation. All it takes is a
Server object that points to a Code42 server.
"""

from datetime import datetime

from c42api.common import resources
from c42api.common import logging_config
from c42api.common.server import Server
from c42api.common import analytics

SCHEMA_VERSION = 1
LOG = logging_config.get_logger(__name__)


@analytics.with_lock
def log_analytics(**kwargs):
    """
    Passes on anything to be logged for analytics.
    """
    analytics.write_json_analytics(__name__, kwargs, result_limit=1)


def fetch_computers(server, params=None, insert_schema_version=False):
    """
    Returns an iterable (specifically a generator) containing json objects
    that represent devices.

    :param server:                A Server object to make the API call to
    :param params:                Params to make the API call with
    :param insert_schema_version: Modify the returned dicts to include the
                                  'schema_version' key.
    """
    start_time = datetime.now().isoformat()
    device_count = 0

    LOG.info('Fetching computer info from %s.',
             server.server_address)
    params = params or {}
    if 'pgSize' not in params:
        params['pgSize'] = str(Server.MAX_PAGE_SIZE)
    devices = server.fetch_all_paged(resources.COMPUTER, params, 'computers')
    for device in devices:
        device_count += 1
        if insert_schema_version:
            device['schema_version'] = SCHEMA_VERSION
        yield device
    LOG.info('Done fetching computer info.')

    end_time = datetime.now().isoformat()
    log_analytics(start_time=start_time,
                  end_time=end_time,
                  device_count=device_count)
