"""Minimaler Onshape-Dokument-Connector."""
import base64
import hashlib
import hmac
import logging
import time
import requests
from odoo import api, fields, models


_logger = logging.getLogger(__name__)

class OnshapeDocument(models.Model):
    """Speichert Dokument-Infos aus Onshape."""

    _name = "onshape.document"
    _description = "Onshape Dokument"

    name = fields.Char(required=True)
    document_id = fields.Char(required=True)

    @api.model
    def _get_credentials(self):
        """Liest API-Schlüssel aus den Systemparametern."""
        params = self.env["ir.config_parameter"].sudo()
        api_key = params.get_param("onshape.api_key")
        api_secret = params.get_param("onshape.api_secret")
        if not api_key or not api_secret:
            raise ValueError("Onshape API Key/Secret nicht gesetzt")
        return api_key, api_secret

    @api.model
    def fetch_documents(self):
        """Lädt Dokumente aus Onshape und speichert sie."""
        api_key, api_secret = self._get_credentials()
        base_url = "https://cad.onshape.com"
        endpoint = "/api/documents"
        method = "GET"
        date = time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime())
        signature_string = f"{method}\n{date}\n{endpoint}\n".encode()
        digest = hmac.new(api_secret.encode(), signature_string, hashlib.sha256).digest()
        signature = base64.b64encode(digest).decode()
        headers = {"Date": date, "Authorization": f"On {api_key}:{signature}"}


        try:
            response = requests.get(base_url + endpoint, headers=headers, timeout=10)
            response.raise_for_status()
        except requests.RequestException:
            _logger.exception("Fehler beim Abrufen der Onshape-Dokumente")
            return False

        for doc in response.json().get("items", []):
            vals = {"name": doc["name"], "document_id": doc["id"]}
            existing = self.search([("document_id", "=", doc["id"])], limit=1)
            if existing:
                existing.write(vals)
            else:
                self.create(vals)
        return True

        response = requests.get(base_url + endpoint, headers=headers, timeout=10)
        response.raise_for_status()
        for doc in response.json().get("items", []):
            self.create({"name": doc["name"], "document_id": doc["id"]})

