"""Query a system for a list of objects for further work."""

from c42api.common import logging_config
from c42api.common import resources
from c42api import computers


LOG = logging_config.get_logger(__name__)


def organization(server, org_name=None):
    """
    Get a single organization that matches a query string.

    :param server (common.Server): Server for making queries against.
    :param org_name (str):         Name of organization to be searched.

    :return object: An Org object for the found organizaion.

    :raise ValueError: An organization with org_name could not be found.

    :todo: This function should be revised to externally look similar to
               `devices()`
    """
    LOG.debug("Querying organization information.")

    org_params = {}
    if org_name:
        org_params['q'] = org_name
    response = server.get(resources.ORG, org_params)
    binary = type(server).json_from_response(response)
    orgs = binary['data']['orgs']

    if len(orgs) == 0:
        raise ValueError("No organizations found with the name '%s'." % org_name)

    return orgs[0]


def devices(server, queries=None, device_type="CrashPlan"):
    """
    Get all devices that match a list of query strings.

    :param server (common.Server): Server for making queries against.
    :param queries (list[str]):    List of `str` queries, where organization
                                       searches begin with "org:"
    :param device_type (str):      Device type to filter when calculating list.

    :return list[int]: A list of deviceGUID's matching any of the queries.
    """
    device_list = []
    if not queries:
        LOG.debug("Querying all computers inside system.")
        response = computers.fetch_computers(server)
        device_list = [x['guid'] for x in response if x['service'] == device_type]
        if len(device_list) == 0:
            LOG.warn("No active computers could be found in this Code42 system.")
    else:
        if not isinstance(queries, list):
            queries = [queries]

        for query in queries:
            params = {'active': 'true'}

            if query.startswith('org:'):
                org_query = query[4:]
                # Querying organization information
                org_uid = organization(server, org_query)['orgUid']

                LOG.debug("Querying all computers inside organization " + org_uid + ".")
                # Querying all computers inside organization.
                params['orgUid'] = org_uid
            else:
                LOG.debug("Querying computers with name " + query + ".")
                # Querying all computers inside organization.
                params['q'] = query

            LOG.debug("Querying all computers inside system.")
            response = computers.fetch_computers(server, params)
            device_list = [x['guid'] for x in response if x['service'] == device_type]

            if len(device_list) == 0:
                LOG.error("Computer " + query + " could not be found, or is not active.")

    LOG.debug('Found ' + str(len(device_list)) + ' devices matching queries.')
    return device_list
