from napalm import get_network_driver

from lib.action import NapalmBaseAction


class NapalmGetNTP(NapalmBaseAction):
    """Get NTP details from a network device via NAPALM
    """

    def run(self, hostname, host_ip, driver, port, credentials, query_type, htmlout=False):

        try:
            # Look up the driver  and if it's not given from the configuration file
            # Also overides the hostname since we might have a partial host i.e. from
            # syslog such as host1 instead of host1.example.com
            #
            (hostname,
             host_ip,
             driver,
             credentials) = self.find_device_from_config(hostname, host_ip, driver, credentials)

            login = self.get_credentials(credentials)

            if not query_type:
                query_type = 'stats'
            else:
                query_type = type.lower()
                if query_type not in ["stats", "servers", "peers"]:
                    raise ValueError(('{} is not a valid ntp query type use: '
                                      'stats, servers or peers.').format(query_type))

            if not port:
                optional_args = None
            else:
                optional_args = {'port': str(port)}

            with get_network_driver(driver)(
                hostname=str(host_ip),
                username=login['username'],
                password=login['password'],
                optional_args=optional_args
            ) as device:

                if type == "stats":
                    ntp_result = {'raw': device.get_ntp_stats()}
                elif type == "servers":
                    ntp_result = {'raw': device.get_ntp_servers()}
                elif type == "peers":
                    ntp_result = {'raw': device.get_ntp_peers()}
                else:
                    raise ValueError(('{} is not a valid ntp query type use: '
                                      'stats, servers or peers.').format(type))

                if htmlout:
                    ntp_result['html'] = self.html_out(ntp_result['raw'])

        except Exception, e:
            self.logger.error(str(e))
            return (False, str(e))

        return (True, ntp_result)
