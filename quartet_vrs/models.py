from django.db import models
from django.utils.translation import gettext_lazy as _


class VRSGS1Locations(models.Model):
    GLN13 = models.CharField(
        max_length=13,
        verbose_name=_("GLN13"),
        help_text=_("A GLN (Global Location Number) that represents a "
                    "Location allowed to execute Verification Requests"
                    ),
        unique=True,
        db_index=True,
        null=True
    )
    active = models.BooleanField(
        default=True,
        verbose_name=_("Active"),
        help_text=_("If the GLN13 is not Active, requests coming from the GLN, e.g. reqGLN=invalid_gtin, will be denied.")
    )

    class Meta:
        db_table = 'quartet_vrs_glns'


class VRSRequest(models.Model):
    GTIN14 = models.CharField(max_length=14,
                              null=False,
                              blank=False,
                              help_text=_('The GTIN 14 from the request.'),
                              verbose_name=_('GTIN 14'))
    lot = models.CharField(
        max_length=20,
        null=False,
        blank=False,
        help_text=_('Lot/Batch'),
        verbose_name=_('Lot/Batch')
    )
    expiry = models.DateField(
        null=False,
        blank=False,
        verbose_name=_('Expiration Date'),
        help_text=('The expiration date of the item being verified.')
    )
    serial_number = models.CharField(
        null=False,
        blank=False,
        verbose_name=_('Serial Number')
    )
    ip_address = models.IPAddressField(
        blank=True,
        verbose_name=_('IP Address'),
        help_text=('The source IP address.')
    )
    header = models.TextField(
        blank=True,
        verbose_name=_('Request Header'),
        help_text=_('The full HTTP request header.')
    )
