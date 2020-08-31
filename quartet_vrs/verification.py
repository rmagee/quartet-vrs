# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Copyright 2019 SerialLab Corp.  All rights reserved.
import logging
import posixpath
import traceback
import urllib.parse
import uuid

import requests
from dateutil.parser import parser
from django.conf import settings
from requests.auth import HTTPBasicAuth
from rest_framework import exceptions
from rest_framework import status

from EPCPyYes.core.v1_2 import helpers
from quartet_epcis.db_api.queries import EPCISDBProxy
from quartet_masterdata.models import TradeItem
from quartet_vrs.models import CompanyAccess
from quartet_vrs.models import GTINMap

logger = logging.getLogger(__name__)


class Verification:
    VERIFICATION_CODE_GTIN_SERIAL = "No_match_GTIN_Serial"
    VERIFICATION_CODE_GTIN_SERIAL_LOT_EXPIRY = "No_match_GTIN_Serial_Lot_Expiry"
    VERIFICATION_CODE_GTIN_SERIAL_LOT = "No_match_GTIN_Serial_Lot"
    VERIFICATION_CODE_GTIN_SERIAL_EXPIRY = "No_match_GTIN_Serial_Expiry"
    VERIFICATION_CODE_NO_REASON = "No_reason_provided"
    VERIFICATION_CODE_GTIN_NOT_REGISTERED = "GTIN_not_registered"
    VERIFICATION_CODE_GTIN_NOT_FOUND = "GTIN_not_found"

    def __init__(self) -> None:
        super().__init__()
        self.parser = parser()

    def check_connectivity(self, gtin: str, req_gln: str,
                           context: str = "dscsaSaleableReturn"):
        """
                   The checkConnectivity method enables a check of connectivity with the QU4RTET verification service and returns
                   the appropriate HTTP status code. If the Requestor GLN (reqGLN) is not recognized, QU4RTET verification service will
                   respond with an HTTP 401 'Unauthorized' response. If the Requestor GLN (reqGLN) is not permitted to make requests, the verification
                   service will respond with an HTTP 403 'Forbidden' response.

                   :param request: HTTP Request
                   :param gtin: GS1 GTIN 14
                   :param context: Default is dscsaSaleableReturn
            """
        try:
            company_access = CompanyAccess.objects.get(company__GLN13=req_gln)
            gtin = TradeItem.objects.get(GTIN14=gtin)
            if not company_access.access_granted:
                raise exceptions.AuthenticationFailed(
                    'The GLN %s does not have access to query this system.'
                    % req_gln, 403)
            if company_access.responder:
                responder_gln = company_access.responder.GLN13
            else:
                responder_gln = getattr(settings, 'DEFAULT_VRS_RESPONDER_GLN',
                                        None)
                if not responder_gln:
                    raise exceptions.APIException(
                        'Please configure a default responder for '
                        'the system and/or configure a responder '
                        'GLN for the company with GLN %s.' %
                        req_gln, status=500
                    )
            return responder_gln
        except CompanyAccess.DoesNotExist:
            raise exceptions.NotAuthenticated(
                'The GLN %s is not configured for access.' % req_gln, 401)
        except TradeItem.DoesNotExist:
            raise exceptions.APIException(
                'The GTIN %s is not available for query on '
                'this system.' % gtin,
                404
            )

    def _check_connectivity_external(self, gtin: str, req_gln: str,
                                     context: str = "dscsaSaleableReturn"):

        try:
            map = GTINMap.objects.get(gtin=gtin)
            if map.use_ssl:
                protocol = "https://"
            else:
                protocol = "http://"

            if map.port is not None and map.port != "443" and map.port != "80":
                host = "{0}{1}:{2}".format(protocol, map.host, map.port)
            else:
                host = "{0}{1}".format(protocol, map.host)

            path = posixpath.join(map.path,
                                  "checkConnectivity?gtin={0}&reqGLN={1}".format(
                                      gtin, req_gln))

            logger.info(
                'checkConnectivity using External VRS at {0}'.format(host))
            url = urllib.parse.urljoin(host, path)

            if map.user_name is not None:
                response = requests.get(url, auth=HTTPBasicAuth(map.user_name,
                                                                map.password))
            else:
                response = requests.get(url)
            if response.status_code != status.HTTP_200_OK:
                raise Exception(response.content)

            ret_val = response.json()
            # Add the external VRS host
            ret_val['location'] = map.host

        except GTINMap.DoesNotExist:
            desc = 'GTIN: {0} is not mapped to an external VRS'.format(gtin)
            logger.error(desc)
            ret_val = self._verification_message(
                response_gln="",
                correlation_id="",
                verified=False,
                reason=Verification.VERIFICATION_CODE_GTIN_NOT_FOUND,
                description=desc
            )
        except Exception as e:
            desc = 'Unable to verify GTIN: {0} using external VRS at {0}'.format(
                gtin, host)
            logger.error(desc)
            ret_val = self._verification_message(
                response_gln="",
                correlation_id="",
                verified=False,
                reason=Verification.VERIFICATION_CODE_GTIN_NOT_FOUND,
                description=desc
            )

        return ret_val

    def verify(self, gtin: str, lot: str, serial_number: str, correlation_id: str,
               exp: str, linkType: str, context: str, reqGLN):
        '''
        Static Method used to Verify GTIN-14, Lot, and Serial Number
        :param gtin: GS1 GTIN-14
        :param lot: Lot Number
        :param serial_number: Serial Number
        :param correlation_id: Correlation ID
        :param exp: Expiry Date as String
        :return: Returns a Verification Message explaining the Verification Results
        '''

        ret_val = None
        company_prefix = None
        response_gln = None
        lot_matched = False
        exp_matched = False

        if linkType and linkType != 'verificationService':
            raise exceptions.APIException('An invalid linkType was specified '
                                          'in the URl.',400)
        if context and context != 'dscsaSaleableReturn':
            raise exceptions.APIException('An invalid context was specified '
                                          'in the URL', 400)

        if not getattr(settings, 'VRS_ALLOW_ALL_REQ_GLNS', False):
            ca = CompanyAccess.objects.filter(company__GLN13=reqGLN).exists()
            if not ca:
                raise exceptions.NotAuthenticated(
                    'The reqGLN %s is not authorized to query this '
                    'system.' % reqGLN, 401)
            else:
                ca = CompanyAccess.objects.get(company__GLN13 = reqGLN)
                response_gln = ca.responder if ca.responder else \
                    getattr(settings, 'DEFAULT_VRS_RESPONDER_GLN')


        if correlation_id is None or len(correlation_id) == 0:
            correlation_id = str(uuid.uuid4())
        try:
            trade_item = TradeItem.objects.select_related().get(GTIN14=gtin)
            company_prefix = trade_item.company.gs1_company_prefix
            if not response_gln:
                response_gln = trade_item.company.GLN13
        except TradeItem.DoesNotExist:
            try:
                # The TradeItem is not in master data. Send to a Remote VRS
                logger.info('Contacting External VRS')
                return self._verify_external(gtin, lot, serial_number,
                                                     correlation_id, exp)
            except:
                tb = traceback.format_exc()
                logger.error(tb)
                # Build Response
                ret_val = self._verification_message(
                    response_gln=response_gln,
                    correlation_id=correlation_id,
                    verified=False,
                    reason=Verification.VERIFICATION_CODE_GTIN_NOT_FOUND
                )
        except Exception:
            # Whatever Exception happens here, the GTIN was not found.
            # Log Exception

            tb = traceback.format_exc()
            logger.error(tb)
            # Build Response
            ret_val = self._verification_message(
                response_gln=response_gln,
                correlation_id=correlation_id,
                verified=False,
                reason=Verification.VERIFICATION_CODE_GTIN_SERIAL
            )

        if company_prefix is not None:
            # Transform the GTIN into an EPC URN Id
            indicator_digit = gtin[0]
            item_ref = gtin[len(company_prefix) + 1: -1]
            epc = "urn:epc:id:sgtin:{0}.{1}{2}.{3}".format(company_prefix,
                                                           indicator_digit,
                                                           item_ref,
                                                           serial_number)

            # Search Repo for EPC, Serial Number, Lot, Expiry
            db_proxy = EPCISDBProxy()
            # If events are returned, consider GTIN and Serial Number Verified
            try:
                events = db_proxy.get_events_by_entry_identifer(
                    entry_identifier=epc)

                if len(events) == 0:
                    # No events means GTIN & Serial Number could not be verified
                    ret_val = self._verification_message(
                        response_gln=response_gln,
                        correlation_id=correlation_id,
                        verified=False,
                        reason=Verification.VERIFICATION_CODE_GTIN_SERIAL
                    )
            except Exception as e:
                # Log Exception
                tb = traceback.format_exc()
                logger.error(tb)
                # Whatever the reason, the GTIN & Serial Number could not be verified
                ret_val = self._verification_message(
                    response_gln=response_gln,
                    correlation_id=correlation_id,
                    verified=False,
                    reason=Verification.VERIFICATION_CODE_GTIN_SERIAL
                )

            for event in events:
                # Get the Event and loop through the ilmd elements, if they exist.
                evt = db_proxy.get_event_by_id(event_id=event.event_id)
                if hasattr(evt, 'ilmd'):
                    for md in evt.ilmd:
                        if md.name == "lotNumber" and md.value == lot:
                            lot_matched = True
                        elif md.name == 'itemExpirationDate':
                            exp_matched = exp == self._format_exp_date(md.value)
                if exp_matched and lot_matched:
                    break

            if ret_val is None:
                # GTIN & SerialNumber have matched
                if exp_matched and lot_matched:
                    # GTIN, Serial, Lot, and Expiry all Verified.
                    ret_val = self._verification_message(
                        response_gln=response_gln,
                        correlation_id=correlation_id
                    )

                elif not exp_matched and not lot_matched:
                    # The Lot and/or Expiry could not be verified.
                    # The GTIN & Serial did not match the Lot and Expiry
                    ret_val = self._verification_message(
                        response_gln=response_gln,
                        correlation_id=correlation_id,
                        verified=False,
                        reason=Verification.VERIFICATION_CODE_GTIN_SERIAL_LOT_EXPIRY
                    )

                elif not exp_matched and lot_matched:
                    # The Expiry could not be verified.
                    # The GTIN & Serial did not match the Expiry
                    ret_val = self._verification_message(
                        response_gln=response_gln,
                        correlation_id=correlation_id,
                        verified=False,
                        reason=Verification.VERIFICATION_CODE_GTIN_SERIAL_EXPIRY
                    )

                elif exp_matched and not lot_matched:
                    # The Lot could not be verified.
                    # The GTIN & Serial did not match the Lot
                    ret_val = self._verification_message(
                        response_gln=response_gln,
                        correlation_id=correlation_id,
                        verified=False,
                        reason=Verification.VERIFICATION_CODE_GTIN_SERIAL_LOT
                    )
        # Return the Response
        return ret_val


    def _verify_external(self, gtin: str, lot: str, serial_number: str,
                         correlation_id: str, exp: str):

        try:
            map = GTINMap.objects.get(gtin=gtin)
            if map.use_ssl:
                protocol = "https://"
            else:
                protocol = "http://"

            if map.port is not None and map.port != "443" and map.port != "80":
                host = "{0}{1}:{2}".format(protocol, map.host, map.port)
            else:
                host = "{0}{1}".format(protocol, map.host)

            path = posixpath.join(map.path,
                                  "verify/gtin/{0}/lot/{1}/ser/{2}?exp={3}".format(
                                      gtin, lot, serial_number, exp))

            logger.info('Verifing using External VRS at {0}'.format(host))
            url = urllib.parse.urljoin(host, path)

            if map.user_name is not None:
                response = requests.get(url, auth=HTTPBasicAuth(map.user_name,
                                                                map.password))
            else:
                response = requests.get(url)
            if response.status_code != status.HTTP_200_OK:
                raise Exception(response.content)

            ret_val = response.json()
            # Add the external VRS host
            ret_val['location'] = map.host

        except GTINMap.DoesNotExist:
            desc = 'GTIN: {0} is not mapped to an external VRS'.format(gtin)
            logger.error(desc)
            ret_val = self._verification_message(
                response_gln="",
                correlation_id=correlation_id,
                verified=False,
                reason=Verification.VERIFICATION_CODE_GTIN_NOT_FOUND,
                description=desc
            )
        except Exception as e:
            desc = 'Unable to verify GTIN: {0} using external VRS at {0}'.format(
                gtin, host)
            logger.error(desc)
            ret_val = self._verification_message(
                response_gln="",
                correlation_id=correlation_id,
                verified=False,
                reason=Verification.VERIFICATION_CODE_GTIN_NOT_FOUND,
                description=desc
            )

        return ret_val

    def _verification_message(self, response_gln: str,
                              correlation_id: str = "",
                              verified: bool = True,
                              reason: str = VERIFICATION_CODE_NO_REASON,
                              additional_info: bool = False,
                              location: str = '',
                              description: str = ''):
        '''
        Static Method that builds a Verification Message, with or without Additional Information.
        :param correlation_id: Correlation UUID provided by Requestor
        :param additional_info: If True, will provide additional information.
        :return: JSON str
        '''

        now, _ = helpers.get_current_utc_time_and_offset()
        if verified:
            if not additional_info:
                ret_val = {
                    "verificationTimestamp": now,
                    "responderGLN": response_gln,
                    "data": {"verified": verified},
                    "corrUUID": correlation_id
                }
            else:
                ret_val = {
                    "verificationTimestamp": now,
                    "responderGLN": response_gln,
                    "data": {
                        "verified": verified,
                        "additionalInfo": "recalled"
                        # Only additional info in the Light Weight Message Spec v1.0.2
                    },
                    "corrUUID": correlation_id
                }
        else:
            # Not Verified messages
            if not additional_info:
                ret_val = {
                    "verificationTimestamp": now,
                    "responderGLN": response_gln,
                    "data": {
                        "verified": verified,
                        "verificationFailureReason": reason
                    },
                    "corrUUID": correlation_id
                }
            else:
                ret_val = {
                    "verificationTimestamp": now,
                    "responderGLN": response_gln,
                    "data": {
                        "verified": verified,
                        "verificationFailureReason": reason,
                        "additionalInfo": "recalled"
                        # Only additional info in the Light Weight Message Spec v1.0.2
                    },
                    "corrUUID": correlation_id,

                }
            if len(location) > 0:
                ret_val['location'] = location
            if len(description) > 0:
                ret_val["description"] = description
        return ret_val

    def _format_exp_date(self, date):
        dt = self.parser.parse(date)
        return dt.strftime('%y%m%d')
