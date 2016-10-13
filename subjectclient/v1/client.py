# Copyright 2012 OpenStack Foundation
# Copyright 2013 IBM Corp.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import logging

from keystoneauth1.exceptions import catalog as key_ex

from subjectclient import client
from subjectclient import exceptions
from subjectclient.i18n import _LE
from subjectclient.v1 import agents
from subjectclient.v1 import aggregates
from subjectclient.v1 import availability_zones
from subjectclient.v1 import certs
from subjectclient.v1 import cloudpipe
from subjectclient.v1 import fixed_ips
from subjectclient.v1 import flavor_access
from subjectclient.v1 import flavors
from subjectclient.v1 import floating_ip_dns
from subjectclient.v1 import floating_ip_pools
from subjectclient.v1 import floating_ips
from subjectclient.v1 import floating_ips_bulk
from subjectclient.v1 import fping
from subjectclient.v1 import hosts
from subjectclient.v1 import hypervisors
from subjectclient.v1 import images
from subjectclient.v1 import keypairs
from subjectclient.v1 import limits
from subjectclient.v1 import networks
from subjectclient.v1 import quota_classes
from subjectclient.v1 import quotas
from subjectclient.v1 import security_group_default_rules
from subjectclient.v1 import security_group_rules
from subjectclient.v1 import security_groups
from subjectclient.v1 import server_groups
from subjectclient.v1 import server_migrations
from subjectclient.v1 import subjects
from subjectclient.v1 import services
from subjectclient.v1 import usage
from subjectclient.v1 import versions
from subjectclient.v1 import virtual_interfaces
from subjectclient.v1 import volumes


class Client(object):
    """Top-level object to access the OpenStack Compute API.

    .. warning:: All scripts and projects should not initialize this class
      directly. It should be done via `subjectclient.client.Client` interface.
    """

    def __init__(self, username=None, api_key=None, project_id=None,
                 auth_url=None, insecure=False, timeout=None,
                 proxy_tenant_id=None, proxy_token=None, region_name=None,
                 endpoint_type='publicURL', extensions=None,
                 service_type='subject', service_name=None,
                 volume_service_name=None, timings=False, bypass_url=None,
                 os_cache=False, no_cache=True, http_log_debug=False,
                 auth_system='keystone', auth_plugin=None, auth_token=None,
                 cacert=None, tenant_id=None, user_id=None,
                 connection_pool=False, session=None, auth=None,
                 api_version=None, direct_use=True, logger=None, **kwargs):
        """Initialization of Client object.

        :param str username: Username
        :param str api_key: API Key
        :param str project_id: Project ID
        :param str auth_url: Auth URL
        :param bool insecure: Allow insecure
        :param float timeout: API timeout, None or 0 disables
        :param str proxy_tenant_id: Tenant ID
        :param str proxy_token: Proxy Token
        :param str region_name: Region Name
        :param str endpoint_type: Endpoint Type
        :param str extensions: Extensions
        :param str service_type: Service Type
        :param str service_name: Service Name
        :param str volume_service_name: Volume Service Name
        :param bool timings: Timings
        :param str bypass_url: Bypass URL
        :param bool os_cache: OS cache
        :param bool no_cache: No cache
        :param bool http_log_debug: Enable debugging for HTTP connections
        :param str auth_system: Auth system
        :param str auth_plugin: Auth plugin
        :param str auth_token: Auth token
        :param str cacert: cacert
        :param str tenant_id: Tenant ID
        :param str user_id: User ID
        :param bool connection_pool: Use a connection pool
        :param str session: Session
        :param str auth: Auth
        :param api_version: Compute API version
        :param direct_use: Inner variable of subjectclient. Do not use it outside
            subjectclient. It's restricted.
        :param logger: Logger
        :type api_version: subjectclient.api_versions.APIVersion
        """
        if direct_use:
            raise exceptions.Forbidden(
                403, _LE("'subjectclient.v1.client.Client' is not designed to be "
                         "initialized directly. It is inner class of "
                         "subjectclient. You should use "
                         "'subjectclient.client.Client' instead. Related lp "
                         "bug-report: 1493576"))

        # FIXME(comstud): Rename the api_key argument above when we
        # know it's not being used as keyword argument

        # NOTE(cyeoh): In the subjectclient context (unlike Nova) the
        # project_id is not the same as the tenant_id. Here project_id
        # is a name (what the Nova API often refers to as a project or
        # tenant name) and tenant_id is a UUID (what the Nova API
        # often refers to as a project_id or tenant_id).

        password = kwargs.pop('password', api_key)
        self.projectid = project_id
        self.tenant_id = tenant_id
        self.user_id = user_id
        self.flavors = flavors.FlavorManager(self)
        self.flavor_access = flavor_access.FlavorAccessManager(self)
        self.images = images.ImageManager(self)
        self.glance = images.GlanceManager(self)
        self.limits = limits.LimitsManager(self)
        self.servers = subjects.ServerManager(self)
        self.versions = versions.VersionManager(self)

        # extensions
        self.agents = agents.AgentsManager(self)
        self.dns_domains = floating_ip_dns.FloatingIPDNSDomainManager(self)
        self.dns_entries = floating_ip_dns.FloatingIPDNSEntryManager(self)
        self.cloudpipe = cloudpipe.CloudpipeManager(self)
        self.certs = certs.CertificateManager(self)
        self.floating_ips = floating_ips.FloatingIPManager(self)
        self.floating_ip_pools = floating_ip_pools.FloatingIPPoolManager(self)
        self.fping = fping.FpingManager(self)
        self.volumes = volumes.VolumeManager(self)
        self.keypairs = keypairs.KeypairManager(self)
        self.networks = networks.NetworkManager(self)
        self.neutron = networks.NeutronManager(self)
        self.quota_classes = quota_classes.QuotaClassSetManager(self)
        self.quotas = quotas.QuotaSetManager(self)
        self.security_groups = security_groups.SecurityGroupManager(self)
        self.security_group_rules = \
            security_group_rules.SecurityGroupRuleManager(self)
        self.security_group_default_rules = \
            security_group_default_rules.SecurityGroupDefaultRuleManager(self)
        self.usage = usage.UsageManager(self)
        self.virtual_interfaces = \
            virtual_interfaces.VirtualInterfaceManager(self)
        self.aggregates = aggregates.AggregateManager(self)
        self.hosts = hosts.HostManager(self)
        self.hypervisors = hypervisors.HypervisorManager(self)
        self.hypervisor_stats = hypervisors.HypervisorStatsManager(self)
        self.services = services.ServiceManager(self)
        self.fixed_ips = fixed_ips.FixedIPsManager(self)
        self.floating_ips_bulk = floating_ips_bulk.FloatingIPBulkManager(self)
        self.os_cache = os_cache or not no_cache
        self.availability_zones = \
            availability_zones.AvailabilityZoneManager(self)
        self.server_groups = server_groups.ServerGroupsManager(self)
        self.server_migrations = \
            server_migrations.ServerMigrationsManager(self)

        # Add in any extensions...
        if extensions:
            for extension in extensions:
                if extension.manager_class:
                    setattr(self, extension.name,
                            extension.manager_class(self))

        if not logger:
            logger = logging.getLogger(__name__)

        self.client = client._construct_http_client(
            username=username,
            password=password,
            user_id=user_id,
            project_id=project_id,
            tenant_id=tenant_id,
            auth_url=auth_url,
            auth_token=auth_token,
            insecure=insecure,
            timeout=timeout,
            auth_system=auth_system,
            auth_plugin=auth_plugin,
            proxy_token=proxy_token,
            proxy_tenant_id=proxy_tenant_id,
            region_name=region_name,
            endpoint_type=endpoint_type,
            service_type=service_type,
            service_name=service_name,
            volume_service_name=volume_service_name,
            timings=timings,
            bypass_url=bypass_url,
            os_cache=self.os_cache,
            http_log_debug=http_log_debug,
            cacert=cacert,
            connection_pool=connection_pool,
            session=session,
            auth=auth,
            api_version=api_version,
            logger=logger,
            **kwargs)

    @property
    def api_version(self):
        return self.client.api_version

    @api_version.setter
    def api_version(self, value):
        self.client.api_version = value

    @client._original_only
    def __enter__(self):
        self.client.open_session()
        return self

    @client._original_only
    def __exit__(self, t, v, tb):
        self.client.close_session()

    @client._original_only
    def set_management_url(self, url):
        self.client.set_management_url(url)

    def get_timings(self):
        return self.client.get_timings()

    def reset_timings(self):
        self.client.reset_timings()

    def has_neutron(self):
        """Check the service catalog to figure out if we have neutron.

        This is an intermediary solution for the window of time where
        we still have subject-network support in the client, but we
        expect most people have neutron. This ensures that if they
        have neutron we understand, we talk to it, if they don't, we
        fail back to subject proxies.
        """
        try:
            endpoint = self.client.get_endpoint(service_type='network')
            if endpoint:
                return True
            return False
        except key_ex.EndpointNotFound:
            return False

    @client._original_only
    def authenticate(self):
        """Authenticate against the server.

        Normally this is called automatically when you first access the API,
        but you can call this method to force authentication right now.

        Returns on success; raises :exc:`exceptions.Unauthorized` if the
        credentials are wrong.
        """
        self.client.authenticate()
