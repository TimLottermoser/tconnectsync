#!/usr/bin/env python3

import unittest
from unittest.mock import patch

from tconnectsync.sync.tandemsource.update_profiles import UpdateProfiles
from tconnectsync.domain.tandemsource.pump_settings import PumpSettings

from ...api.fake import TConnectApi
from ...nightscout_fake import NightscoutApi

DEVICE_ID = '1114157'

# Trimmed real BFF settings.details shape (from the captured bff/pumper
# response). Values condensed; PumpSettings.from_dict is patched in these
# tests, so we only assert it is reached with this blob — parsing the new
# shape is covered when PumpSettings is migrated.
SETTINGS_DETAILS = {
    'basalLimitSettings': {'basalLimitDefault': 5000, 'basalLimit': 5000},
    'globalMaxBolusSettings': {'maxBolus': 25000, 'maxBolusDefault': 25000},
    'profiles': {'numberOfProfiles': 1, 'activeSegment': 0, 'activeIdp': 0, 'profile': []},
}


def _meta(device_id=DEVICE_ID, settings=None):
    return {
        'deviceId': device_id,
        'serialNumber': '1518994',
        'modelNumber': '1004000',
        'modelName': 'Tandem Mobi™ System',
        'softwareVersion': '1.0.0.0',
        'algorithm': 'Control-IQ',
        'maxDateWithEvents': '2026-05-27T23:03:06',
        'minDateWithEvents': '2020-01-02T00:00:00',
        'settings': settings,
    }


class _ReachedFromDict(Exception):
    pass


class FakeTandemSourceApi:
    def __init__(self, metadata):
        self._metadata = metadata

    def pump_metadata(self):
        return self._metadata

    def needs_relogin(self):
        # Required so TConnectApi.tandemsource returns this fake, not a real API.
        return False


class TestUpdateProfilesSettingsSourcing(unittest.TestCase):
    maxDiff = None

    def _updater(self, metadata, device_id=DEVICE_ID):
        tconnect = TConnectApi()
        tconnect._tandemsource = FakeTandemSourceApi(metadata)
        nightscout = NightscoutApi()
        return UpdateProfiles(tconnect, nightscout, device_id, pretend=True)

    def test_matching_device_with_settings_reaches_from_dict(self):
        updater = self._updater([_meta(settings=SETTINGS_DETAILS)])
        # Sentinel proves we pass the guard and hand settings.details to from_dict.
        with patch.object(PumpSettings, 'from_dict', side_effect=_ReachedFromDict) as fd:
            with self.assertRaises(_ReachedFromDict):
                updater.update(pretend=True)
        fd.assert_called_once_with(SETTINGS_DETAILS)

    def test_matching_device_with_null_settings_returns_false(self):
        updater = self._updater([_meta(settings=None)])
        with patch.object(PumpSettings, 'from_dict') as fd:
            result = updater.update(pretend=True)
        self.assertFalse(result)
        fd.assert_not_called()

    def test_no_device_match_returns_false(self):
        updater = self._updater([_meta(device_id='some-other-device', settings=SETTINGS_DETAILS)])
        with patch.object(PumpSettings, 'from_dict') as fd:
            result = updater.update(pretend=True)
        self.assertFalse(result)
        fd.assert_not_called()

    def test_empty_metadata_returns_false(self):
        updater = self._updater([])
        with patch.object(PumpSettings, 'from_dict') as fd:
            result = updater.update(pretend=True)
        self.assertFalse(result)
        fd.assert_not_called()


if __name__ == "__main__":
    unittest.main()
