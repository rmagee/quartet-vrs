# -*- coding: utf-8 -*-
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
from django.db import models
from django.utils.translation import gettext_lazy as _
from model_utils import models as utils
from model_utils import Choices

VRS_CONTEXT = (
                'dscsaSaleableReturn', 'dscsaSaleableReturn'
              ),

class VRSConfig(utils.TimeStampedModel):
    '''
    Configuration Values for the VRS REST API
    '''
    gtin = models.CharField(
        max_length=14,
        null=False,
        help_text=_()
    )
    response_gln = models.CharField(
        max_length=13,
        null=False,
        help_text=_('The GLN representing the entity/location responding to a VRS request.'),
        verbose_name=_('Responder GLN'),
        unique=True,
    ),
    request_gln = models.CharField(
        max_length=50,
        null=False,
        help_text=_('The GLN representing the entity/location making a VRS request.'),
        verbose_name=_('Request Context'),

    ),
    context = Choices('dscsaSaleableReturn', )

