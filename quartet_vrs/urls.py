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
from django.conf.urls import url


from . import views

app_name = 'quartet_vrs'

urlpatterns = [
    url(
        r'^checkConnectivity$',
        views.CheckConnectivityView.as_view(),
        name="checkConnectivity"
    ),
    # The verify url is http(s)://www.example.com/gtin/{gtin}/lot/{lot}/ser/{ser}?exp={exp}
    url(
        r'^verify/gtin/(?P<gtin>[0-9]{14})/lot/(?P<lot>[\w{}.-]*)/ser/(?P<serial_number>[\w{}.-]*)$',
        views.VerifyView.as_view(), name="verify"
    )


]

