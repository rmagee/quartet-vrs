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
import os, io, uuid, json
import django
from django.contrib.auth.models import Group, User
from rest_framework.test import force_authenticate
from rest_framework.test import APITestCase
from rest_framework.test import APIRequestFactory, APIClient
from django.urls import reverse
from mixer.backend.django import mixer
from quartet_vrs.verification import Verification
from quartet_masterdata.models import TradeItem, Company
from quartet_epcis.parsing.parser import QuartetParser
from quartet_vrs.management.commands.create_vrs_groups import Command
from quartet_vrs.views import GTINMapView, CheckConnectivityView, VerifyView
from quartet_vrs.models import GTINMap

os.environ['DJANGO_SETTINGS_MODULE'] = 'tests.settings'
django.setup()


class ViewTest(APITestCase):

    def setUp(self):
        #these values match the values in tests/data/commission.xml

        self.gtin = "03055555555557"
        self.request_gln = "3055551234562"
        self.response_gln = "3055551234562"
        self.serial_number = "1"
        self.lot_number = "DL232"
        self.expiry_date = "20151231"
        self.company_prefix = "305555"
        self.invalid_gln = "0359767999914"


        user = User.objects.create_superuser(username='testuser',
                                        password='unittest',
                                        email='testuser@seriallab.local')
        Command().handle()
        oag = Group.objects.get(name='VRS Access')
        user.groups.add(oag)
        user.save()
        self.client.force_authenticate(user=user)
        self.user = user

        # Build a Test Company
        company = mixer.blend(Company, gs1_company_prefix=self.company_prefix, GLN13=self.response_gln)
        # Build a Test TradeItem
        mixer.blend(TradeItem, company = company, GTIN14=self.gtin)
        # Build a GTIN Map
        mixer.blend(GTINMap, gtin = "00000000000001",
            host="test.qu4rtet.io",
            path="/vrs",
            gs1_complian=True,
            use_ssl=True)

        # Get the test data file
        dir = os.path.dirname(os.path.abspath(__file__))
        file_name = "commission.xml"
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
        factory = APIRequestFactory()
        user = User.objects.get(username='testuser')
        view = CheckConnectivityView.as_view()
        request = factory.get("/checkConnectivity/?gtin={0}&reqGLN={1}".format(self.gtin, self.invalid_gln))
        force_authenticate(request, user=user)
        response = view(request)
        self.assertEquals(response.status_code, 401)

    def test_check_connectivity_200(self):
        factory = APIRequestFactory()
        user = User.objects.get(username='testuser')
        view = CheckConnectivityView.as_view()
        request = factory.get("/checkConnectivity/?gtin={0}&reqGLN={1}".format(self.gtin, self.request_gln))
        force_authenticate(request, user=user)
        response = view(request)
        self.assertEquals(response.status_code, 200)

    def test_verify_200(self):

        corrID = str(uuid.uuid4())

        user = User.objects.get(username='testuser')
        client = APIClient()
        client.force_authenticate(user=user)

        url = reverse('verify', kwargs=
            {'gtin': self.gtin,
             'lot': self.lot_number,
             'serial_number':self.serial_number
            })
        url += "?exp={0}&corrUUID={1}".format(self.expiry_date, corrID)

        response = client.get(url)

        self.assertEquals(response.status_code, 200)
        msg = response.data

        self.assertEquals(msg["responderGLN"], self.response_gln)
        self.assertEquals(msg["corrUUID"], corrID)
        self.assertIsNotNone(msg["verificationTimestamp"])

        data = msg["data"]
        self.assertEquals(data["verified"], True)

    def test_verify_unverified(self):

        # # Provide bogus GTIN
        url = reverse("verify", kwargs={'gtin': "00000000000014", 'lot': self.lot_number, 'serial_number': self.serial_number})
        # Add Expiration Date
        corrID = str(uuid.uuid4())
        url = url + "?exp=" + self.expiry_date
        url = url + "&corrUUID=" + corrID

        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        msg = response.json()
        self.assertEquals(msg["data"]["verified"], False)

    def test_verify_invalid_serial_number(self):

        # # An invalid serial number should return unverified
        # # Provide bogus GTIN
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
        # An invalid lot should return unverified
        # Provide Real GTIN
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

    def test_gtin_map(self):

        data = {
            "gtin": "00000000000019",
            "host": "test2.qu4rtet.io",
            "path":"/vrs",
            "gs1_compliant":True,
            "use_ssl":False

        }
        factory = APIRequestFactory()
        user = User.objects.get(username='testuser')
        view = GTINMapView.as_view({'post':'create'})
        request = factory.post('/gtinmap/', data)
        force_authenticate(request, user=user)
        response = view(request)
        self.assertEquals(response.status_code, 201)

    def test_retrieve_from_gtin_map(self):

        gtin = "00000000000001"

        user = User.objects.get(username='testuser')
        client = APIClient()
        client.force_authenticate(user=user)

        url = reverse('gtinmap-detail',kwargs={'pk':1})
        url +=  "?gtin={0}".format(gtin)

        response = client.get(url)
        self.assertEquals(response.status_code, 200)

