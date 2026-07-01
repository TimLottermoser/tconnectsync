#!/usr/bin/env python3

import unittest
from unittest.mock import patch

from tconnectsync.api.tandemsource import TandemSourceApi


# Representative GET api/reports/bff/pumper/{pumperId} response, mirroring the
# structure of a real captured account response: one active pump with settings
# and one never-uploaded pump (null date/settings fields).
BFF_PUMPER = {
    "firstName": "Test",
    "lastName": "User",
    "name": "Test User",
    "dateOfBirth": "1990-01-01",
    "lowGlucoseThreshold": 70,
    "highGlucoseThreshold": 180,
    "country": "US",
    "pumps": [
        {
            "algorithm": "Control-IQ",
            "availableDataRange": {"start": "2021-05-06T12:31:19", "end": "2022-02-16T22:45:58"},
            "assignmentId": "1b493210-9336-4901-a329-a352775738c5",
            "lastUploadDate": "2022-09-20T05:50:12Z",
            "maxDateOfEvents": "2022-02-16T22:45:58",
            "modelNumber": "1000354",
            "modelName": "t:slim X2™ Insulin Pump",
            "partNumber": "1011979",
            "serialNumber": "90556643",
            "softwareVersion": "7.8.0.0",
            "lastUploadClientType": "mobile_tconnect",
            "settings": {
                "id": "b7f931c8-63cd-44c9-86aa-56826f9057e5",
                "deviceAssignmentId": "1b493210-9336-4901-a329-a352775738c5",
                "uploadedTimeStamp": "2022-09-10T21:07:43.497",
                "settingsHash": "29EDDA8E7A72C1AD060271268CC7AE81FAD54B9D",
                "uploadId": "5da6a0ca-86c3-440f-9462-fa53168dcb9d",
                "details": {"profiles": {"numberOfProfiles": 1}},
            },
        },
        {
            "algorithm": "Basal-IQ",
            "availableDataRange": {"start": None, "end": None},
            "assignmentId": "f6631fff-f403-4ce4-9362-83eff9e2850e",
            "glucoseUnit": None,
            "lastUploadDate": None,
            "maxDateOfEvents": None,
            "modelNumber": "1000096",
            "modelName": "t:slim X2™ Insulin Pump",
            "partNumber": "1003314",
            "serialNumber": "514387",
            "softwareVersion": "6.0.3.0",
            "lastUploadClientType": None,
            "settings": None,
        },
    ],
}


class TestPumpMetadataAdapter(unittest.TestCase):
    maxDiff = None

    def _api(self):
        # Bypass __init__ (which performs a network login) to test the adapter.
        return TandemSourceApi.__new__(TandemSourceApi)

    def test_bff_pump_to_metadata_active_pump(self):
        meta = TandemSourceApi._bff_pump_to_metadata(BFF_PUMPER["pumps"][0])
        self.assertEqual(meta["deviceId"], "1b493210-9336-4901-a329-a352775738c5")
        self.assertEqual(meta["serialNumber"], "90556643")
        self.assertEqual(meta["modelNumber"], "1000354")
        self.assertEqual(meta["softwareVersion"], "7.8.0.0")
        self.assertEqual(meta["algorithm"], "Control-IQ")
        # maxDateOfEvents -> maxDateWithEvents
        self.assertEqual(meta["maxDateWithEvents"], "2022-02-16T22:45:58")
        # availableDataRange.start -> minDateWithEvents
        self.assertEqual(meta["minDateWithEvents"], "2021-05-06T12:31:19")
        # settings.details -> settings
        self.assertEqual(meta["settings"], {"profiles": {"numberOfProfiles": 1}})

    def test_bff_pump_to_metadata_never_uploaded_pump(self):
        meta = TandemSourceApi._bff_pump_to_metadata(BFF_PUMPER["pumps"][1])
        self.assertEqual(meta["deviceId"], "f6631fff-f403-4ce4-9362-83eff9e2850e")
        self.assertEqual(meta["serialNumber"], "514387")
        # null date/settings fields map to None, not KeyError
        self.assertIsNone(meta["maxDateWithEvents"])
        self.assertIsNone(meta["minDateWithEvents"])
        self.assertIsNone(meta["settings"])

    def test_pump_metadata_maps_all_pumps(self):
        api = self._api()
        with patch.object(TandemSourceApi, "get_pumper", return_value=BFF_PUMPER):
            metas = api.pump_metadata()
        self.assertEqual(len(metas), 2)
        self.assertEqual(
            [m["deviceId"] for m in metas],
            [
                "1b493210-9336-4901-a329-a352775738c5",
                "f6631fff-f403-4ce4-9362-83eff9e2850e",
            ],
        )

    def test_pump_metadata_empty_when_no_pumps(self):
        api = self._api()
        with patch.object(TandemSourceApi, "get_pumper", return_value={}):
            self.assertEqual(api.pump_metadata(), [])


if __name__ == "__main__":
    unittest.main()
