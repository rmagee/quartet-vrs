# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

import os
from django.conf.urls import url
from django.urls import include, path
from rest_framework import routers
from quartet_vrs import views


router = routers.DefaultRouter()
router.register(r'gtinmap', views.GTINMapView)

app_name = 'quartet_vrs'

urlpatterns = [
    url(
        r'^checkConnectivity$',
        views.CheckConnectivityView.as_view(),
        name="checkConnectivity"
    ),
    # The verify url is http(s)://www.example.com/gtin/{gtin}/lot/{lot}/ser/{ser}?exp={exp}
    url(
        r'^verify/gtin/(?P<gtin>[0-9]{14})/lot/(?P<lot>[\w{}.-]*)/ser/(?P<serial_number>[\x21-\x22\x25-\x2F\x30-\x39\x3A-\x3F\x41-\x5A\x5F\x61-\x7A]{0,20})/?$',
        views.VerifyView.as_view(), name="verify"
    ),
    path('', include(router.urls))
]

import pprint
pprint.pprint(urlpatterns)
