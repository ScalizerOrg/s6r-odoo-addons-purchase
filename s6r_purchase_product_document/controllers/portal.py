# Copyright 2026 Scalizer (<https://www.scalizer.fr>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import http
from odoo.exceptions import AccessError, MissingError
from odoo.http import request
from odoo.http.stream import content_disposition

from odoo.addons.purchase.controllers import portal as purchase_portal


class CustomerPortal(purchase_portal.CustomerPortal):
    def _purchase_order_get_page_view_values(self, order, access_token, **kwargs):
        """Add the documents shared with the vendor to the portal page."""
        values = super()._purchase_order_get_page_view_values(order, access_token, **kwargs)
        order_sudo = order.sudo()
        values.update(
            {
                "purchase_documents": order_sudo._get_purchase_documents(),
                "purchase_bom_lines": order_sudo._get_purchase_bom_lines(),
            }
        )
        return values

    def _get_purchase_order_sudo(self, order_id, access_token):
        """Return the order if the current user can access it.

        :param order_id: purchase.order id
        :param access_token: access token of the order
        :return: purchase.order record (sudo) or None
        """
        try:
            return self._document_check_access("purchase.order", order_id, access_token=access_token)
        except (AccessError, MissingError):
            return None

    @http.route(
        "/my/purchase/<int:order_id>/document/<int:document_id>",
        type="http",
        auth="public",
        website=True,
        readonly=True,
    )
    def portal_purchase_document(self, order_id, document_id, access_token=None, **kwargs):
        """Download a product document shared with the vendor."""
        order_sudo = self._get_purchase_order_sudo(order_id, access_token)
        if not order_sudo:
            return request.redirect("/my")
        document = request.env["product.document"].sudo().browse(document_id).exists()
        if not document or document not in order_sudo._get_purchase_documents():
            return request.redirect("/my")
        if document.type == "url":
            return request.redirect(document.url, local=False)
        return (
            request.env["ir.binary"]
            ._get_stream_from(document.ir_attachment_id)
            .get_response(as_attachment=True)
        )

    @http.route(
        "/my/purchase/<int:order_id>/bom/<int:line_id>",
        type="http",
        auth="public",
        website=True,
    )
    def portal_purchase_bom(self, order_id, line_id, access_token=None, **kwargs):
        """Download the PDF of a subcontracting BoM shared with the vendor."""
        order_sudo = self._get_purchase_order_sudo(order_id, access_token)
        if not order_sudo:
            return request.redirect("/my")
        line = order_sudo._get_purchase_bom_lines().filtered(lambda line: line.id == line_id)
        if not line:
            return request.redirect("/my")
        name, content = line._get_bom_pdf()
        return request.make_response(
            content,
            headers=[
                ("Content-Type", "application/pdf"),
                ("Content-Length", len(content)),
                ("Content-Disposition", content_disposition(name)),
            ],
        )
