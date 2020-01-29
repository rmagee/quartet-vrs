# -*- coding: utf-8 -*-
import os
import socket
import dns.resolver
from dns.resolver import NXDOMAIN
from logging import getLogger

logger = getLogger()

class Conductor:

    def __init__(self, zone=None):
        self.zone = zone or os.getenv('ZONE')
        if not self.zone:
            raise self.NoZoneDefined(
                'You must define a ZONE in either '
                'your .env file, the constructor parameter'
                ' or in a local environment variable.'
            )

    def resolve(self, gtin, port=80):
        """
        Resolves a GTIN to an IP address.
        :param gtin:
        :param port:
        :return:
        """
        host_name = self._host_name(gtin)
        logger.debug('Will resolve from hostname %s', host_name)
        try:
            vrs_address = socket.gethostbyname(
                host_name
            )
        except socket.gaierror:
            logger.exception('The host %s could not be resolved.  Make'
                             ' sure this is a valid entry in the provided '
                             'zone.')
            raise

    def _host_name(self, gtin):
        #return 'gtin%s.%s' % (gtin, self.zone)
        return '%s.%s' % (gtin, self.zone)

    def resolve_ex(self, gtin):
        ret = []
        try:
            record = dns.resolver.query(self._host_name(gtin), 'A')
            if record:
                for data in record:
                    ret.append(data)
        except dns.resolver.NXDOMAIN:
            record = dns.resolver.query(self._host_name(gtin), 'CNAME')
            if record:
                for rdata in record:
                    ret.append(rdata.target)

        return ret

    class NoZoneDefined(Exception):
        pass
