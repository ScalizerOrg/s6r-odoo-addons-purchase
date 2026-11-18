# Copyright 2026 Scalizer (<https://www.scalizer.fr>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from markupsafe import Markup

from odoo import models

SIGNATURE_MARKER = "<div>--"


class MailComposeMessage(models.TransientModel):
    _inherit = "mail.compose.message"

    def _get_purchase_document_order(self):
        """Return the purchase order whose documents are added to the email.

        :return: purchase.order record (sudo) or None
        """
        self.ensure_one()
        if (
            not self.env.context.get("purchase_product_documents")
            or self.model != "purchase.order"
            or self.composition_mode != "comment"
        ):
            return None
        res_ids = self._evaluate_res_ids()
        if len(res_ids) != 1:
            return None
        return self.env["purchase.order"].browse(res_ids).sudo()

    def _compute_body(self):
        """Add the download links of the shared documents to the body."""
        res = super()._compute_body()
        for composer in self.filtered("template_id"):
            order = composer._get_purchase_document_order()
            if not order:
                continue
            documents = order._get_purchase_documents()
            bom_lines = order._get_purchase_bom_lines()
            if not documents and not bom_lines:
                continue
            links = self.env["ir.qweb"].with_context(lang=composer.lang or self.env.lang)._render(
                "s6r_purchase_product_document.mail_purchase_documents",
                {"order": order, "documents": documents, "bom_lines": bom_lines},
            )
            body = str(composer.body or "")
            index = body.find(SIGNATURE_MARKER)
            if index == -1:
                body += str(links)
            else:
                body = body[:index] + str(links) + body[index:]
            composer.body = Markup(body)  # noqa: S704 - body and links are already sanitized
        return res

    def _compute_attachment_ids(self):
        """Attach the shared files which are not included in the order PDF."""
        res = super()._compute_attachment_ids()
        for composer in self.filtered("template_id"):
            order = composer._get_purchase_document_order()
            if not order:
                continue
            files = order._get_purchase_document_attachments(composer.template_id.report_template_ids[:1])
            if not files:
                continue
            attachments = self.env["ir.attachment"].create(
                [
                    {
                        "name": name,
                        "raw": content,
                        "res_model": "mail.compose.message",
                        "res_id": 0,
                        "type": "binary",
                    }
                    for name, content in files
                ]
            )
            composer.attachment_ids = composer.attachment_ids | attachments
        return res
