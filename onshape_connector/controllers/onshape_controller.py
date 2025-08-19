"""HTTP-Controller für die Synchronisation."""
from odoo import http


class OnshapeController(http.Controller):
    @http.route("/onshape/sync", type="http", auth="user", csrf=False)
    def sync_onshape(self):
        http.request.env["onshape.document"].sudo().fetch_documents()
        return http.Response("Synchronisation abgeschlossen", status=200)
