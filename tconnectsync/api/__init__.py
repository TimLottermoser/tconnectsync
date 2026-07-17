import logging

from .tandemsource import TandemSourceApi

logger = logging.getLogger(__name__)

"""A wrapper for the Tandem Source API."""
class TConnectApi:
    email = None
    password = None

    def __init__(self, email, password, region='EU'):
        self.email = email
        self.password = password
        self.region = region
        self._tandemsource = None
        # --- KLARTEXT DEBUG IN __INIT__ ---
        logger.warning(f"DEBUG [__init__] EMAIL: '{email}' | PASSWORD: '{password}' | REGION: '{region}'")

    @property
    def tandemsource(self):
        if self._tandemsource and not self._tandemsource.needs_relogin():
            return self._tandemsource

        logger.debug(f"Instantiating new TandemSourceApi for region {self.region}")
        
        # --- KLARTEXT DEBUG VOR DEM LOGIN-VERSUCH ---
        logger.warning(f"DEBUG [tandemsource] LOGIN-START -> EMAIL: '{self.email}' | PASSWORD: '{self.password}' | REGION: '{self.region}'")
        
        self._tandemsource = TandemSourceApi(self.email, self.password, self.region)
        return self._tandemsource
