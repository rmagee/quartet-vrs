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
import os, io, uuid
import django
from django.contrib.auth.models import Group, User
from mixer.backend.django import mixer
from rest_framework.test import APITestCase
from django.urls import reverse
from quartet_vrs.verification import Verification
from quartet_vrs.models import VRSGS1Locations
from quartet_masterdata.models import TradeItem, Company
from quartet_epcis.parsing.parser import QuartetParser
from quartet_vrs.management.command.create_vrs_groups import Command


os.environ['DJANGO_SETTINGS_MODULE'] = 'tests.settings'
django.setup()


class ViewTest(APITestCase):

    def setUp(self):
        # these values match the values in tests/data/shipping.xml
        self.gtin = "00359767016015"
        self.request_gln = "0359767000014"
        self.response_gln = "0876543219876"
        self.serial_number = "100000000011"
        self.lot_number = "A123456"
        self.expiry_date = "191130"
        self.company_prefix = "0359767"
        self.invalid_gln = "0359767999914"
        self.inactive_gln = "0359767888814"

        user = User.objects.create_user(username='testuser',
                                        password='unittest',
                                        email='testuser@seriallab.local')
        Command().handle()
        oag = Group.objects.get(name='VRS Access')
        user.groups.add(oag)
        user.save()
        self.client.force_authenticate(user=user)
        self.user = user

        # Build a Test Company
        company = mixer.blend(Company, gs1_company_prefix=self.company_prefix, GLN13=self.response_gln, SGLN="urn:epc:id:sgln:0359767.00001")
        # Build a Test TradeItem
        mixer.blend(TradeItem, company = company, GTIN14=self.gtin)
        # Build a Test GLN to 'whitelist' for Verification Request
        mixer.blend(VRSGS1Locations, GLN13=self.request_gln)
        # Build an Inactive, Whitelisted GLN
        mixer.blend(VRSGS1Locations, GLN13=self.inactive_gln, active=False)
        # Get the test data file
        dir = os.path.dirname(os.path.abspath(__file__))
        file_name = "shipping.xml"
        path = os.path.join(os.path.join(dir, "data"), file_name)

        # parse EPCIS Data
        with open(path, "rb") as epcis_doc:
            epcis_bytes = io.BytesIO(epcis_doc.read())
            parser = QuartetParser(stream=epcis_bytes)
            parser.parse()

    def test_check_connectivity_401(self):
        '''
        Test with Correct GTIN and Invalid Request GLN
        :return:
        '''
        url = reverse("checkConnectivity")
        url = url + "?gtin={0}&reqGLN={1}".format(self.gtin, self.invalid_gln)
        response = self.client.get(url)
        self.assertEquals(response.status_code, 401)

    def test_check_connectivity_inactive_gln_401(self):
        '''
        Test with Correct GTIN and Inactive Request GLN
        :return:
        '''
        url = reverse("checkConnectivity")
        url = url + "?gtin={0}&reqGLN={1}".format(self.gtin, self.inactive_gln)
        response = self.client.get(url)
        self.assertEquals(response.status_code, 403)

    def test_check_connectivity_200(self):

        url = reverse("checkConnectivity")
        url = url + "?gtin={0}&reqGLN={1}".format(self.gtin, self.request_gln)

        response = self.client.get(url)
        self.assertIs(response.status_code, 200)
        data = response.json()
        gln = data["responderGLN"]
        self.assertEquals(gln, "0876543219876" )

    def test_gln_inactive(self):

        url = reverse("checkConnectivity")
        url = url + "?gtin={0}&reqGLN={1}".format("01234567890129", "0321012345678")

        response = self.client.get(url)
        self.assertEquals(response.status_code, 401)

    def test_verify_200(self):

        url = reverse("verify", kwargs={'gtin':self.gtin, 'lot':self.lot_number, 'serial_number':self.serial_number })
        # Add Experiation Date
        corrID = str(uuid.uuid4())
        url = url + "?exp=" +  self.expiry_date
        url = url + "&corrUUID=" + corrID

        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        msg = response.json()
        self.assertEquals(msg["responderGLN"], self.response_gln)
        self.assertEquals(msg["corrUUID"], corrID)
        self.assertIsNotNone(msg["verificationTimestamp"])
        data = msg["data"]
        self.assertEquals(data["verified"], True)

    def test_verify_unverified(self):

        # Provide bogus GTIN
        url = reverse("verify", kwargs={'gtin': "00000000000000", 'lot': self.lot_number, 'serial_number': self.serial_number})
        # Add Expiration Date
        corrID = str(uuid.uuid4())
        url = url + "?exp=" + self.expiry_date
        url = url + "&corrUUID=" + corrID

        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        msg = response.json()
        self.assertEquals(msg["data"]["verified"], False)

    def test_verify_invalid_serial_number(self):
        # An invalid serial number should return unverified
        # Provide bogus GTIN
        url = reverse("verify", kwargs={'gtin': self.gtin, 'lot': self.lot_number, 'serial_number': "000000000000"})
        # Add Expiration Date
        corrID = str(uuid.uuid4())
        url = url + "?exp=" + self.expiry_date
        url = url + "&corrUUID=" + corrID

        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        msg = response.json()
        self.assertEquals(msg["responderGLN"], self.response_gln)
        self.assertEquals(msg["corrUUID"], corrID)
        self.assertIsNotNone(msg["verificationTimestamp"])
        data = msg["data"]
        self.assertEquals(data["verified"], False) # Should not be verified
        self.assertEquals(data["verificationFailureReason"], Verification.VERIFICATION_CODE_GTIN_SERIAL)

    def test_verify_invalid_lot(self):
        # An invalid serial number should return unverified
        # Provide bogus GTIN
        url = reverse("verify", kwargs={'gtin': self.gtin, 'lot': "000000", 'serial_number': self.serial_number})
        # Add Expiration Date
        corrID = str(uuid.uuid4())
        url = url + "?exp=" + self.expiry_date
        url = url + "&corrUUID=" + corrID

        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        msg = response.json()
        self.assertEquals(msg["responderGLN"], self.response_gln)
        self.assertEquals(msg["corrUUID"], corrID)
        self.assertIsNotNone(msg["verificationTimestamp"])
        data = msg["data"]
        self.assertEquals(data["verified"], False) # Should not be verified
        self.assertEquals(data["verificationFailureReason"], Verification.VERIFICATION_CODE_GTIN_SERIAL_LOT)
