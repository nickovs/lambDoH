# lambDoH DNS client

"""
This file implements the code to take an incoming DNS request packet,
send it to various DNS servers seeking and answer and return the first
successful answer.
"""

import logging
import random
import time
import socket

import dns.message
import dns.query

LOGGER = logging.getLogger("__app__")

DEFAULT_SERVERS = ['8.8.8.8', '8.8.4.4']

def _read_resolve_conf():
    servers = []
    try:
        for line in open("/etc/resolv.conf"):
            line = line.strip()
            if line and line[0] != '#':
                parts = line.split()
                if parts[0] == 'nameserver' and len(parts) > 1:
                    servers.append(parts[1])
    # pylint: disable=broad-except
    except Exception as ex:
        LOGGER.error("Failed to read resolve.conf")
        LOGGER.info("Exception details: %s", ex)
    return servers

# pylint: disable=too-few-public-methods
class DNSClient:
    """A syncronous DNS lookup client"""
    def __init__(self, servers, shuffle=False, timeout=5.0):
        self._shuffle = shuffle
        self._timeout = timeout
        """Initialise the with a list comma-separated list of servers"""
        if servers and servers.strip():
            self._server_list = [ip.strip() for ip in servers.split(',')]
        else:
            self._server_list = _read_resolve_conf()

        if not self._server_list:
            LOGGER.error("No DNS config found; using defaults.")
            self._server_list = DEFAULT_SERVERS

        LOGGER.info("Intialised DNS client with server list: %s",
                    self._server_list)

    def resolve_dns_query(self, request_packet):
        """Take a wire-format DNS request and return a wire-format reply"""
        query = dns.message.from_wire(request_packet)
        LOGGER.debug("Query details: %s", query.to_text())

        if self._shuffle:
            random.shuffle(self._server_list)

        end_limit = time.time() + self._timeout

        reply = None
        # Take a copy, since we might whitle this down
        server_list = self._server_list[:]

        while reply is None:
            if not server_list:
                LOGGER.error("No servers left to try")
                return b''
            # Loop over a copy, since the server list might change
            for server in server_list[:]:
                timeout = end_limit - time.time()
                if timeout <= 0:
                    LOGGER.info("DNS request timed out")
                    break
                try:
                    reply = dns.query.udp(query, self._server_list[0], timeout)
                except (socket.error, dns.exception.Timeout) as ex:
                    LOGGER.error("Socket error: %s", ex)
                    reply = None
                    continue
                except dns.query.UnexpectedSource as ex:
                    LOGGER.error("Very odd response: %s", ex)
                    reply = None
                    continue
                except dns.exception.FormError as ex:
                    LOGGER.error("Bed reply from server %s: %s", server, ex)
                    server_list.remove(server)
                    reply = None
                    continue

                if reply is not None:
                    break

        if not reply:
            # Note that we explicitly do NOT log the failing query at `warning`
            # level as this might be a privacy issue
            LOGGER.warning("No reply to query")
        else:
            LOGGER.debug("Reply details: %s", reply.to_text())

        return reply.to_wire() if reply else b''
