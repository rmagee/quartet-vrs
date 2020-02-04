from django.db import models
from django.utils.translation import gettext_lazy as _


class GTINMap(models.Model):
    gtin = models.CharField(
        max_length=14,
        verbose_name=_("GTIN"),
        help_text=_("A GTIN that represents a "
                    "Trade Item"
                    ),
        unique=True,
        db_index=True,
        null=False
    )
    path = models.CharField(
        max_length=256,
        verbose_name=_("Path"),
        help_text=_("The Sub Path of the VRS Service. For Example: If the URL path is http://vrs.qu4rtet.io/vrs, then the path is: /vrs."
                    " The compliant portion of the path, e.g. /verify/ or /checkConnectivity/ etc., is NOT required here, unless"
                    " the path is NOT GS1 Compliant as indicated int 'GS1 Compliant' field below."),
        null=True,
        blank=True
    )
    host = models.CharField(
        max_length=256,
        verbose_name=_("Hostname"),
        help_text=_("The Hostname of the VRS Router. If the URL is https://vrs.qu4rtet.io, then the host is: vrs.qu4rtet.io."),
        null=False
    )
    port = models.CharField(
        max_length=10,
        verbose_name=_("Port"),
        help_text=_("Port Number to use when calling external VRS. NOTE: Port is NOT required when Port Number is 443 or 80"),
        null=True,
        blank=True
    )
    user_name = models.CharField(
        max_length=100,
        verbose_name=_("Username"),
        help_text=_(
            "The Username for the VRS Router."),
        null=True,
        blank = True
    )
    password = models.CharField(
        max_length=100,
        verbose_name=_("Password"),
        help_text=_(
            "The Password for the VRS Router."),
        null=True,
        blank=True
    )
    gs1_compliant = models.BooleanField(
        default=True,
        verbose_name=_("GS1 Compliant"),
        help_text=_("True if the VRS Router is compliant with GS1.")
    )
    use_ssl = models.BooleanField(
        default=True,
        verbose_name=_("Use SSL"),
        help_text=_("True if the VRS Router should use SSL when connecting to the host and path.")
    )

    class Meta:
        db_table = 'quartet_vrs_gtin_map'


class RequestLog(models.Model):
    remote_address = models.CharField(
        max_length=14,
        verbose_name=_("Remote Address"),
        help_text=_("IP Address of the server making request."
                    ),
        null=True
    )
    expiry = models.CharField(
        max_length=35,
        verbose_name=_("Expiry Date"),
        help_text=_("Expiry Query Parameter."
                    ),
        null=True
    )
    request_gln = models.CharField(
        max_length=13,
        verbose_name=_("Request GLN"),
        help_text=_("Requestor's GLN."
                    ),
        null=True
    )
    corr_uuid = models.CharField(
        max_length=40,
        verbose_name=_("Correlation UUID"),
        help_text=_("The Correlation Unique Identifier, if used."
                    ),
        null=True
    )
    gtin = models.CharField(
        max_length=14,
        verbose_name=_("GTIN"),
        help_text=_("GTIN Parameter Value for the request."
                    ),
        null=True
    )
    lot = models.CharField(
        max_length=150,
        verbose_name=_("Lot/Batch"),
        help_text=_("Lot or Batch Parameter Value for the request."
                    ),
        null=True
    )
    serial_number = models.CharField(
        max_length=50,
        verbose_name=_("Serial Number"),
        help_text=_("Serial Number Parameter Value for the request."
                    ),
        null=True
    )
    user_name = models.CharField(
        max_length=100,
        verbose_name=_("User Name"),
        help_text=_("Name of user making the request."
                    ),
        null=True
    )
    response = models.TextField(
        verbose_name =_("Response Content"),
        help_text=_("Response from the VRS."),
        null=True
    )
    operation = models.CharField(
        max_length=50,
        verbose_name=_("Operation"),
        help_text=_("The API Operation Requested, checkConnectivity or verify, called with this HTTP Request."
                    ),
        null=True
    )
    success = models.BooleanField(
        null=False,
        default=False,
        verbose_name=_("Success"),
        help_text=_("True if request resulted in a verification or a returned Requestor GLN, False if not."
                    ),
    )
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'quartet_vrs_request_log'
