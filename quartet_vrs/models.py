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
