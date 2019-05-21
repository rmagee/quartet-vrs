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
import traceback
import logging
from rest_framework import status
from rest_framework.response import Response
from EPCPyYes.core.v1_2 import helpers
from quartet_epcis.db_api.queries import EPCISDBProxy
from quartet_masterdata.models import TradeItem
from quartet_vrs.models import VRSGS1Locations

logger = logging.getLogger(__name__)


class Verification():
    VERIFICATION_CODE_GTIN_SERIAL = "No_match_GTIN_Serial"
    VERIFICATION_CODE_GTIN_SERIAL_LOT_EXPIRY = "No_match_GTIN_Serial_Lot_Expiry"
    VERIFICATION_CODE_GTIN_SERIAL_LOT = "No_match_GTIN_Serial_Lot"
    VERIFICATION_CODE_GTIN_SERIAL_EXPIRY = "No_match_GTIN_Serial_Expiry"
    VERIFICATION_CODE_NO_REASON = "No_reason_provided"

    @staticmethod
    def check_connectivity(gtin: str, req_gln: str, context: str="dscsaSaleableReturn"):
        """
                   The checkConnectivity method enables a check of connectivity with the QU4RTET verification service and returns
                   the appropriate HTTP status code. If the Requestor GLN (reqGLN) is not recognised, QU4RTET verification service will
                   respond with an HTTP 401 'Unauthorized' response. If the Requestor GLN (reqGLN) is not permitted to make requests, the verification
                   service will respond with an HTTP 403 'Forbidden' response.

                   :param request: HTTP Request
                   :param gtin: GS1 GTIN 14
                   :param context: Default is dscsaSaleableReturn
            """
        logger.debug("Entering quartet_vrs.check_connectivity()")
        try:
            ret_val = None
            try:
                trade_item = TradeItem.objects.select_related().get(GTIN14=gtin)
                response_gln = trade_item.company.GLN13
                if response_gln != req_gln:
                    req_gln = VRSGS1Locations.objects.get(GLN13=req_gln)
                    if not req_gln.active:
                        ret_val = Response(status=status.HTTP_403_FORBIDDEN, content_type="application/json")
                    else:
                        ret_val = Response(
                            {"responderGLN": response_gln},
                            status=status.HTTP_200_OK,
                            content_type="application/json"
                        )
            except TradeItem.DoesNotExist:
                logger.error('qu4rtet_vrs.checkConnectivity().\r\n No TradeItems match GTIN : %s.' % gtin)
                ret_val = Response(status=status.HTTP_401_UNAUTHORIZED, content_type="application/json")
            except VRSGS1Locations.DoesNotExist:
                logger.error('qu4rtet_vrs.checkConnectivity().\r\n No VRSGS1Locations match reqGLN : %s.' % req_gln)
                ret_val = Response(status=status.HTTP_401_UNAUTHORIZED, content_type="application/json")

        except Exception:
            # Unexpected error, return HTTP 500 Server Error and log the exception
            data = traceback.format_exc()
            logger.error('Exception in qu4rtet_vrs.checkConnectivity().\r\n%s' % data)
            ret_val = Response({"error": "A Server Error occurred servicing this request"},
                               status.HTTP_500_INTERNAL_SERVER_ERROR, content_type="application/json")
        finally:
            # Return Response
            return ret_val

    @staticmethod
    def verify(gtin: str, lot: str, serial_number: str, correlation_id: str, exp: str):
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
        try:
            trade_item = TradeItem.objects.select_related().get(GTIN14=gtin)
            company_prefix = trade_item.company.gs1_company_prefix
            response_gln = trade_item.company.GLN13
        except Exception:
            # Whatever Exception happens here, the GTIN was not found.
            # Log Exception
            tb = traceback.format_exc()
            logger.error(tb)
            # Build Response
            ret_val = Verification._verification_message(
                response_gln=response_gln,
                correlation_id=correlation_id,
                verified=False,
                reason=Verification.VERIFICATION_CODE_GTIN_SERIAL
            )

        if company_prefix is not None:
            # Transform the GTIN into an EPC URN Id
            indicator_digit = gtin[0]
            item_ref = gtin[len(company_prefix) + 1: -1]
            epc = "urn:epc:id:sgtin:{0}.{1}{2}.{3}".format(company_prefix, indicator_digit, item_ref, serial_number)

            # Search Repo for EPC, Serial Number, Lot, Expiry
            db_proxy = EPCISDBProxy()
            # If events are returned, consider GTIN and Serial Number Verified
            try:
                events = None
                events = db_proxy.get_events_by_entry_identifer(entry_identifier=epc)
                if len(events) == 0:
                    # No events means GTIN & Serial Number could not be verified
                    ret_val = Verification._verification_message(
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
                ret_val = Verification._verification_message(
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
                        if not lot_matched and md.value == lot:
                            # Lot Found
                            lot_matched = True
                        if not exp_matched and Verification._format_exp_date(md.value) == exp:
                            # Expiry Found
                            exp_matched = True
                        if exp_matched and lot_matched:
                            # Both Exp and Lot found, so exit the inner loop
                            break
                    if exp_matched and lot_matched:
                        # Both Exp and Lot found, so exit the outer loop
                        break

            if ret_val is None:
                # GTIN & SerialNumber have matched
                if exp_matched and lot_matched:
                    # GTIN, Serial, Lot, and Expiry all Verified.
                    ret_val = Verification._verification_message(
                        response_gln=response_gln,
                        correlation_id=correlation_id
                    )

                elif not exp_matched and not lot_matched:
                    # The Lot and/or Expiry could not be verified.
                    # The GTIN & Serial did not match the Lot and Expiry
                    ret_val = Verification._verification_message(
                        response_gln=response_gln,
                        correlation_id=correlation_id,
                        verified=False,
                        reason=Verification.VERIFICATION_CODE_GTIN_SERIAL_LOT_EXPIRY
                    )

                elif not exp_matched and lot_matched:
                    # The Expiry could not be verified.
                    # The GTIN & Serial did not match the Expiry
                    ret_val = Verification._verification_message(
                        response_gln=response_gln,
                        correlation_id=correlation_id,
                        verified=False,
                        reason=Verification.VERIFICATION_CODE_GTIN_SERIAL_LOT
                    )

                elif exp_matched and not lot_matched:
                    # The Lot could not be verified.
                    # The GTIN & Serial did not match the Lot
                    ret_val = Verification._verification_message(
                        response_gln=response_gln,
                        correlation_id=correlation_id,
                        verified=False,
                        reason=Verification.VERIFICATION_CODE_GTIN_SERIAL_LOT
                    )
        # Return the Response
        return ret_val

    @staticmethod
    def _verification_message(response_gln: str,
                              correlation_id: str = "",
                              verified: bool = True,
                              reason: str = VERIFICATION_CODE_NO_REASON,
                              additional_info: bool = False):
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
                        "additionalInfo": "recalled"  # Only additional info in the Light Weight Message Spec v1.0.2
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
                        "additionalInfo": "recalled"  # Only additional info in the Light Weight Message Spec v1.0.2
                    },
                    "corrUUID": correlation_id
                }
        return ret_val

    @staticmethod
    def _format_exp_date(date):
        if date.find("-") > 0:
            prts = date.split("-")
            if len(prts[0]) == 4:
                prts[0] = prts[0][2:]
            return "{0}{1}{2}".format(prts[0], prts[1], prts[2])
        else:
            return date



