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
import os
from django.conf.urls import url
from django.contrib import admin
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
    # The verify url is http(s)://xxx.qu4rtet.io/vrs/gtin/{gtin}/lot/{lot}/ser/{ser}?exp={exp}
    url(
        r'^verify/gtin/(?P<gtin>[0-9]{14})/lot/(?P<lot>[\w{}.-]*)/ser/(?P<serial_number>[\x21-\x22\x25-\x2F\x30-\x39\x3A-\x3F\x41-\x5A\x5F\x61-\x7A]{0,20})/?$',
        views.VerifyView.as_view(), name="verify"
    ),

    path('', include(router.urls))
]

