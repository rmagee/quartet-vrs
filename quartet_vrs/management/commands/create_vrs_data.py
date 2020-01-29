# This program is free software: you can redistribute it and/| modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, |
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY | FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Copyright 2019 SerialLab Corp.  All rights reserved.
from django.core.management.base import BaseCommand
from django.utils.translation import gettext as _
from quartet_masterdata.models import Company, TradeItem


class Command(BaseCommand):
    help = _('Creates test Master Data for the VRS.')

    def handle(self, *args, **options):
        print('Creating test Data for VRS...')
        company, _ = Company.objects.update_or_create(
            name='Happy Pharma',
            gs1_company_prefix='305555',
            GLN13='3055551234562',
            SGLN='urn:epc:id:sgln:305555.555555.12',
            address1='123 Les Paul Blvd',
            city='Nashville',
            state_province='TN',
            postal_code='08180'

        )

        trade_item, _ = TradeItem.objects.update_or_create(
            company=company,
            GTIN14='03055555555557',

        )

        self.stdout.write(
                self.style.SUCCESS(
                    'Successfully Created VRS Test Master Data\r\n'
                    '=============================================\r\n'
                    '\r\n'
                    'Company Data is:\r\n'
                    '----------------\r\n'
                    'Company Prefix: 305555\r\n'
                    'GLN-13:         3055551234562\r\n'
                    '\r\n'
                    'Trade Item Data is:\r\n'
                    '-------------------\r\n'
                    'GTIN-14:        03055555555557\r\n'
                    '\r\n'
                    'Use these values to test the VRS.'

                )
        )
