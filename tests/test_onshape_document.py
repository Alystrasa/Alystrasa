import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from models.onshape_document import OnshapeDocument


class FakeClient:
    def __init__(self):
        self.updated = False

    def get_document(self, document_id: str) -> dict:
        return {"name": f"Doc {document_id}"}

    def update_document(self, document_id: str, payload: dict):
        self.updated = True
        return {"ok": True}


def test_fetch_and_sync():
    client = FakeClient()
    doc = OnshapeDocument.fetch(client, "123")
    assert doc.name == "Doc 123"
    last_sync = doc.last_sync
    doc.sync(client)
    assert doc.last_sync > last_sync


def test_update_document():
    client = FakeClient()
    doc = OnshapeDocument(name="Initial", onshape_id="1", last_sync=None)
    doc.name = "Updated"
    result = doc.update(client)
    assert client.updated
    assert result["ok"]
