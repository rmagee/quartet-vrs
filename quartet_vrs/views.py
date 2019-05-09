import uuid
from rest_framework.exceptions import NotFound
from rest_framework import status
from rest_framework.renderers import JSONRenderer
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import renderer_classes, api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework import generics
from .models import VRSConfig

logger = logging.getLogger(__name__)


@api_view(http_method_names=['GET'])
@renderer_classes((JSONRenderer,))
def check_connectivity(request, gtin, reqGLN, context):
    """
           Checks the availability of the VRS REST API
           :param request: HTTP Request
    """
    logger.debug("Entering qu4rtet_vrs.check_connectivity()")
    try:

        ret_val = VRSConfig.objects.filter(gtin=gtin, request_gln=reqGLN, context=context)
        return Response({"responderGLN": ret_val.response_gln}, status=status.HTTP_200_OK,
                        content_type="application/json")

    except Exception as e:

        data = traceback.format_exc()
        logger.error('Exception in qu4rtet_vrs.checkConnectivity().\r\n%s' % data)

        return Response({"error": "A Server Error occured servicing this request"},
                        status.HTTP_500_INTERNAL_SERVER_ERROR, content_type="application/json")
