"""Odoo model representing an Onshape document."""

from odoo import api, fields, models

from models.onshape_client import OnshapeClient
from models.onshape_document import OnshapeDocument as DocumentData


class OnshapeDocument(models.Model):
    """Persisted Onshape document in Odoo."""

    _name = "onshape.document"
    _description = "Onshape Document"

    name = fields.Char(required=True)
    onshape_id = fields.Char(required=True)
    last_sync = fields.Datetime()

    def action_sync(self):
        """Synchronize this document with Onshape."""
        client = OnshapeClient()
        for record in self:
            data = DocumentData.fetch(client, record.onshape_id)
            record.write(
                {
                    "name": data.name,
                    "last_sync": fields.Datetime.now(),
                }
            )

    @api.model
    def cron_sync_documents(self):
        """Cron job to synchronize all documents."""
        docs = self.search([])
        docs.action_sync()
        return True
