# Copyright 2026 Scalizer (<https://www.scalizer.fr>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models

from .purchase_order import PDF_MIMETYPE


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    available_bom_ids = fields.Many2many(
        comodel_name="mrp.bom",
        string="Available BoMs",
        compute="_compute_available_bom_ids",
    )
    is_subcontracted = fields.Boolean(compute="_compute_available_bom_ids")
    bom_id = fields.Many2one(
        comodel_name="mrp.bom",
        string="BoM",
        compute="_compute_bom_id",
        store=True,
        readonly=False,
        domain="[('id', 'in', available_bom_ids)]",
        help="Subcontracting bill of materials sent to the vendor with the order.",
    )
    bom_attachment_id = fields.Many2one(
        comodel_name="ir.attachment",
        string="Frozen BoM PDF",
        readonly=True,
        copy=False,
        ondelete="set null",
        help="PDF of the bill of materials generated at the order confirmation.",
    )

    def _get_available_boms(self):
        """Return the subcontracting BoMs of the product for the vendor.

        Only the BoMs without project or with the project of the order are
        returned.

        :return: mrp.bom recordset
        """
        self.ensure_one()
        partner = self.order_id.partner_id
        if self.display_type or not self.product_id or not partner:
            return self.env["mrp.bom"]
        return self.env["mrp.bom"].search(
            [
                ("type", "=", "subcontract"),
                ("company_id", "in", [False, self.order_id.company_id.id]),
                "|",
                ("product_id", "=", self.product_id.id),
                "&",
                ("product_id", "=", False),
                ("product_tmpl_id", "=", self.product_id.product_tmpl_id.id),
                ("subcontractor_ids", "parent_of", partner.ids),
                "|",
                ("project_id", "=", False),
                ("project_id", "=", self.order_id.project_id.id),
            ]
        )

    @api.depends("product_id", "order_id.partner_id", "order_id.project_id")
    def _compute_available_bom_ids(self):
        """Compute the subcontracting BoMs that can be selected."""
        for line in self:
            boms = line._get_available_boms()
            line.available_bom_ids = boms
            line.is_subcontracted = bool(boms)

    @api.depends("product_id", "order_id.partner_id", "order_id.project_id")
    def _compute_bom_id(self):
        """Select the BoM when it is the only one available.

        The BoM of a confirmed order is kept.
        """
        for line in self:
            if line.bom_id and line.state in ("to approve", "purchase", "cancel"):
                line.bom_id = line.bom_id
                continue
            boms = line._get_available_boms()
            if line.bom_id in boms:
                line.bom_id = line.bom_id
            else:
                line.bom_id = boms if len(boms) == 1 else False

    def _get_bom_pdf(self):
        """Return the PDF of the BoM: the frozen one, or a fresh rendering.

        :return: (file name, PDF content) tuple
        """
        self.ensure_one()
        if self.bom_attachment_id:
            attachment = self.bom_attachment_id.sudo()
            return attachment.name, attachment.raw.content if attachment.raw else b""
        name = "%s.pdf" % self.bom_id.display_name.replace("/", "_")
        report = (
            self.company_id.purchase_bom_report_id
            or self.company_id._default_purchase_bom_report_id()
        )
        content, _report_type = (
            self.env["ir.actions.report"]
            .sudo()
            .with_context(lang=self.order_id.partner_id.lang or self.env.lang)
            ._render_qweb_pdf(report, self.bom_id.ids, data={"variant": self.product_id.id})
        )
        return name, content

    def _freeze_bom_pdf(self):
        """Store the PDF of the BoM of the subcontracted lines on the order."""
        for line in self.filtered(
            lambda line: not line.display_type and line.bom_id and not line.bom_attachment_id
        ):
            name, content = line._get_bom_pdf()
            line.bom_attachment_id = self.env["ir.attachment"].create(
                {
                    "name": name,
                    "raw": content,
                    "mimetype": PDF_MIMETYPE,
                    "res_model": "purchase.order",
                    "res_id": line.order_id.id,
                }
            )

    def _unfreeze_bom_pdf(self):
        """Remove the frozen PDF of the BoM."""
        attachments = self.bom_attachment_id
        if attachments:
            self.bom_attachment_id = False
            attachments.unlink()
