"""Onshape document model."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import ClassVar, Optional, Protocol, Any


class OnshapeClientProtocol(Protocol):
    """Protocol describing the minimal interface used by :class:`OnshapeDocument`."""

    def get_document(self, document_id: str) -> dict:
        """Retrieve a document by its identifier."""

    def update_document(self, document_id: str, payload: dict) -> Any:
        """Update a document with the given payload."""


@dataclass
class OnshapeDocument:
    """Representation of an Onshape document.

    Attributes:
        name: Human readable name of the document.
        onshape_id: Unique identifier of the document in Onshape.
        last_sync: Timestamp of the most recent synchronization with Onshape.
    """

    MODEL_NAME: ClassVar[str] = "onshape.document"

    name: str
    onshape_id: str
    last_sync: Optional[datetime] = None

    @classmethod
    def fetch(cls, client: OnshapeClientProtocol, document_id: str) -> "OnshapeDocument":
        """Fetch a document from Onshape using the provided client.

        Args:
            client: Instance capable of communicating with Onshape.
            document_id: The Onshape identifier of the document to fetch.

        Returns:
            An instance of :class:`OnshapeDocument` populated with data from Onshape.
        """
        data = client.get_document(document_id)
        return cls(
            name=data.get("name", ""),
            onshape_id=document_id,
            last_sync=datetime.utcnow(),
        )

    def sync(self, client: OnshapeClientProtocol) -> None:
        """Refresh this document's information from Onshape."""
        data = client.get_document(self.onshape_id)
        self.name = data.get("name", self.name)
        self.last_sync = datetime.utcnow()

    def update(self, client: OnshapeClientProtocol) -> Any:
        """Push local changes of this document to Onshape."""
        payload = {"name": self.name}
        result = client.update_document(self.onshape_id, payload)
        self.last_sync = datetime.utcnow()
        return result
