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
# Copyright 2018 SerialLab Corp.  All rights reserved.
from django.contrib import admin
from quartet_vrs import models

@admin.register(models.GTINMap)
class GTINMapAdmin(admin.ModelAdmin):
    list_display = ('gtin', 'host', 'path', 'gs1_compliant', 'use_ssl')
    ordering = ('gtin',)
def register_to_site(admin_site):
    admin_site.register(models.GTINMap, GTINMapAdmin)
