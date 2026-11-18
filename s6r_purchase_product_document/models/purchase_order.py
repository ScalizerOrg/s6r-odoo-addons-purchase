# Copyright 2026 Scalizer (<https://www.scalizer.fr>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

import io
import zipfile

from odoo import api, fields, models

# Values of `product.document.attached_on_purchase` shared in each order state
PURCHASE_DOCUMENT_VISIBILITY = {
    "draft": ("rfq", "rfq_purchase"),
    "sent": ("rfq", "rfq_purchase"),
    "to approve": ("rfq", "rfq_purchase"),
    "purchase": ("rfq_purchase", "purchase"),
}
PDF_MIMETYPE = "application/pdf"


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    available_product_document_ids = fields.Many2many(
        comodel_name="product.document",
        string="Available Documents",
        compute="_compute_available_product_document_ids",
    )
    document_ids = fields.One2many(
        comodel_name="purchase.order.document",
        inverse_name="order_id",
        string="Documents",
        copy=True,
    )
    document_count = fields.Integer(compute="_compute_document_count")

    @api.depends("order_line.product_id")
    def _compute_available_product_document_ids(self):
        """Compute the documents of the ordered products that can be shared."""
        Document = self.env["product.document"]
        for order in self:
            products = order.order_line.filtered(lambda line: not line.display_type).product_id
            if not products:
                order.available_product_document_ids = Document
                continue
            order.available_product_document_ids = Document.search(
                [
                    ("attached_on_purchase", "!=", "hidden"),
                    "|",
                    "&",
                    ("res_model", "=", "product.product"),
                    ("res_id", "in", products.ids),
                    "&",
                    ("res_model", "=", "product.template"),
                    ("res_id", "in", products.product_tmpl_id.ids),
                ]
            )

    @api.depends("document_ids")
    def _compute_document_count(self):
        """Count the selected documents."""
        for order in self:
            order.document_count = len(order.document_ids)

    # === Documents to share === #

    def _get_purchase_documents(self):
        """Return the selected product documents shared in the current state.

        :return: product.document recordset, in the order of the selection
        """
        self.ensure_one()
        allowed = PURCHASE_DOCUMENT_VISIBILITY.get(self.state, ())
        return self.document_ids.sorted(lambda doc: (doc.sequence, doc.id)).product_document_id.filtered(
            lambda doc: doc.active and doc.attached_on_purchase in allowed
        )

    def _get_purchase_bom_lines(self):
        """Return the order lines whose subcontracting BoM is shared.

        :return: purchase.order.line recordset
        """
        self.ensure_one()
        if self.state == "cancel":
            return self.env["purchase.order.line"]
        return self.order_line.filtered(lambda line: not line.display_type and line.bom_id)

    def _get_purchase_pdf_contents(self):
        """Return the PDF files to append to the order report.

        :return: list of PDF contents (bytes): the BoMs, then the documents
        """
        self.ensure_one()
        contents = [line._get_bom_pdf()[1] for line in self._get_purchase_bom_lines()]
        contents += [
            document.raw.content
            for document in self._get_purchase_documents()
            if document.type == "binary" and document.mimetype == PDF_MIMETYPE
        ]
        return [content for content in contents if content]

    def _get_purchase_document_attachments(self, report=None):
        """Return the files to attach to the email sent to the vendor.

        The PDF files are attached unless they are already appended to the
        report of the email; the other files are gathered in a zip archive.

        :param report: ir.actions.report attached to the email
        :return: list of (file name, content) tuples
        """
        self.ensure_one()
        attachments = []
        if not (report and report in self.company_id.purchase_document_report_ids):
            attachments += [line._get_bom_pdf() for line in self._get_purchase_bom_lines()]
            attachments += [
                (document.name, document.raw.content)
                for document in self._get_purchase_documents()
                if document.type == "binary" and document.mimetype == PDF_MIMETYPE
            ]
        other_documents = self._get_purchase_documents().filtered(
            lambda doc: doc.type == "binary" and doc.mimetype != PDF_MIMETYPE
        )
        if other_documents:
            attachments.append(
                (
                    "%s - %s.zip" % (self.name.replace("/", "_"), self.env._("Documents")),
                    self._zip_documents(other_documents),
                )
            )
        return [(name, content) for name, content in attachments if content]

    @api.model
    def _zip_documents(self, documents):
        """Gather documents in a zip archive.

        :param documents: product.document recordset
        :return: zip archive content (bytes)
        """
        buffer = io.BytesIO()
        names = set()
        with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archive:
            for document in documents:
                name = document.name.replace("/", "_")
                if name in names:
                    name = "%s_%s" % (document.id, name)
                names.add(name)
                archive.writestr(name, document.raw.content if document.raw else b"")
        return buffer.getvalue()

    # === Actions === #

    def action_view_purchase_documents(self):
        """Open the documents selected on the order.

        :return: action dictionary
        """
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": self.env._("Documents"),
            "res_model": "purchase.order.document",
            "view_mode": "list",
            "views": [
                (self.env.ref("s6r_purchase_product_document.purchase_order_document_view_list").id, "list")
            ],
            "domain": [("order_id", "=", self.id)],
            "context": {"default_order_id": self.id},
        }

    def action_preview_purchase_order(self):
        """Display the order as the vendor will see it on the portal.

        :return: URL action dictionary
        """
        self.ensure_one()
        return {
            "type": "ir.actions.act_url",
            "target": "self",
            "url": self.get_portal_url(),
        }

    def action_rfq_send(self):
        """Flag the email composer to add the shared documents."""
        action = super().action_rfq_send()
        action["context"] = dict(action.get("context") or {}, purchase_product_documents=True)
        return action

    def button_approve(self, force=False):
        """Freeze the subcontracting BoM PDF of the confirmed orders."""
        res = super().button_approve(force=force)
        self.filtered(lambda order: order.state == "purchase").order_line._freeze_bom_pdf()
        return res

    def button_draft(self):
        """Release the frozen BoM PDF, it is generated again at confirmation."""
        res = super().button_draft()
        self.order_line._unfreeze_bom_pdf()
        return res
