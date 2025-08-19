from odoo import http
from odoo.http import request


class OnshapeSyncController(http.Controller):
    """Controller providing an endpoint to manually trigger Onshape sync."""

    @http.route("/onshape/sync", type="json", auth="user")
    def manual_sync(self):
        """Manually trigger synchronization of all Onshape documents."""
        docs = request.env["onshape.document"].sudo()
        docs.cron_sync_documents()
        return {"status": "ok"}
