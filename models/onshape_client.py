import base64
import hmac
import os
import uuid
from email.utils import formatdate
from hashlib import sha256
from typing import Any, Dict, Optional

import requests


class OnshapeClient:
    """Simple client for interacting with the Onshape API.

    The client uses HMAC-SHA256 signatures as documented by Onshape to
    authenticate every request. API keys are loaded from environment
    variables ``ONSHAPE_ACCESS_KEY`` and ``ONSHAPE_SECRET_KEY`` unless
    explicitly provided.
    """

    def __init__(
        self,
        access_key: Optional[str] = None,
        secret_key: Optional[str] = None,
        base_url: Optional[str] = None,
    ) -> None:
        self.access_key = access_key or os.getenv("ONSHAPE_ACCESS_KEY")
        self.secret_key = secret_key or os.getenv("ONSHAPE_SECRET_KEY")
        if not self.access_key or not self.secret_key:
            raise ValueError("Onshape API keys not provided.")

        self.base_url = base_url or os.getenv(
            "ONSHAPE_BASE_URL", "https://cad.onshape.com/api"
        )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _build_signature(
        self, method: str, path: str, query: str = "", content_type: str = ""
    ) -> Dict[str, str]:
        """Create authorization headers for a request."""
        nonce = uuid.uuid4().hex
        date = formatdate(timeval=None, usegmt=True)
        canonical = "\n".join([method.upper(), nonce, date, path, query])
        digest = hmac.new(
            self.secret_key.encode("utf-8"), canonical.encode("utf-8"), sha256
        ).digest()
        signature = base64.b64encode(digest).decode("utf-8")

        headers = {
            "Date": date,
            "On-Nonce": nonce,
            "Authorization": f"On {self.access_key}:{signature}",
        }
        if content_type:
            headers["Content-Type"] = content_type
        return headers

    def _request(
        self,
        method: str,
        path: str,
        params: Optional[Dict[str, str]] = None,
        content_type: str = "",
    ) -> Any:
        """Perform an HTTP request against the Onshape API."""
        query = ""
        if params:
            # Sort parameters for canonical query string
            query = "&".join(
                f"{k}={v}" for k, v in sorted(params.items()) if v is not None
            )
        headers = self._build_signature(method, path, query, content_type)
        url = f"{self.base_url}{path}"
        response = requests.request(
            method, url, params=params, headers=headers, timeout=30
        )
        response.raise_for_status()
        return response.json()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def get_document(self, document_id: str) -> Any:
        """Retrieve a document description."""
        path = f"/documents/{document_id}"
        return self._request("GET", path)

    def get_part(self, studio_id: str, element_id: str) -> Any:
        """Retrieve part information from a Part Studio element."""
        path = f"/partstudios/d/{studio_id}/e/{element_id}"
        return self._request("GET", path)
