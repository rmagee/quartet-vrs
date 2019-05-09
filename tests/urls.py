# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

from django.conf.urls import url, include

from quartet_vrs.urls import urlpatterns as quartet_vrs_urls

app_name = 'quartet_vrs'

urlpatterns = [
    url(r'^', include(quartet_vrs_urls)),
]
