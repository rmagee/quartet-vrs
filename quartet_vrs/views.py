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
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .verification import Verification
from quartet_vrs.models import VRSGS1Locations


logger = logging.getLogger(__name__)


class CheckConnectivityView(APIView):

    queryset = VRSGS1Locations.objects.none()

    def get(self, request):
        '''
         The checkConnectivity method enables a check of connectivity with the QU4RTET verification service and returns
         the appropriate HTTP status code. If the Requestor GLN (reqGLN) is not recognised, QU4RTET verification service will
         respond with an HTTP 401 'Unauthorized' response. If the Requestor GLN (reqGLN) is not permitted to make requests, the verification
         service will respond with an HTTP 403 'Forbidden' response.

         Usage:

            http[s]://[host]:[port]/vrs/checkConnectivity?gtin=GTIN14&reqGLN=GLN13[&context=dscsaSaleableReturn]

         :param request: HTTP Request
         :return: respone: HTTP Response
        '''

        gtin = request.GET.get('gtin', '')
        reqGLN = request.GET.get('reqGLN', '')
        context = request.GET.get('context', 'dscsaSaleableReturn')
        return Verification.check_connectivity(gtin=gtin, req_gln=reqGLN, context=context)


class VerifyView(APIView):

    queryset = VRSGS1Locations.objects.none()

    def get(self, request, *args, **kwargs):
        """
        Verifies a product instance by GTIN, Lot, Serial Number, and Expiration Date.

        usage:
        http[s]://[host]:[port]/vrs/verify/gtin/{GTIN14}/lot/{LOT NUMBER]/ser/{SERIAL NUMBER}?exp={Expiry Date e.g. 190401}

        :param request: HTTP Request
        :param gtin: GTIN to verify
        :param lot: Lot number to verify
        :param serial_number: Serial Number to verify
        :return:
        """
        try:

            ret_val = None
            # Get URL embedded Params
            gtin = kwargs.get('gtin', None)
            lot = kwargs.get('lot', None)
            serial_number = kwargs.get('serial_number', None)
            # Get Querystring Params
            exp = request.GET.get('exp', '')
            correlation_id = request.GET.get('corrUUID', '')
            # Verify
            verification_message = Verification.verify(gtin=gtin,
                                lot=lot,
                                serial_number=serial_number,
                                correlation_id=correlation_id,
                                exp=exp)
            # Build Response
            ret_val = Response(
                                verification_message,
                                status=status.HTTP_200_OK,
                                headers={'Cache-Control': 'private, no-cache'},
                                content_type="application/json"
            )
        except Exception:
            # Exception Occurred, return 401
            tb = traceback.format_exc()
            logger.error(tb)
            ret_val = Response(
                            status=status.HTTP_401_UNAUTHORIZED,
                            headers={'Cache-Control': 'private, no-cache'},
                            content_type="application/json"
            )

        finally:
            # return built response
            return ret_val


