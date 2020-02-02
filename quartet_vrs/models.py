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
        help_text=_("The Sub Path of the VRS Service. For Example: If the URL path is http://vrs.qu4rtet.io/vrs, then the path is: /vrs"),
        unique=False,
        null=True
    )
    host = models.CharField(
        max_length=256,
        verbose_name=_("Hostname"),
        help_text=_("The Hostname of the VRS Router. If the URL is https://vrs.qu4rtet.io, then the host is: vrs.qu4rtet.io."),
        unique=True,
        db_index=True,
        null=False
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
