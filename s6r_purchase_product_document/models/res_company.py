# Copyright 2026 Scalizer (<https://www.scalizer.fr>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    purchase_document_report_ids = fields.Many2many(
        comodel_name="ir.actions.report",
        relation="res_company_purchase_document_report_rel",
        column1="company_id",
        column2="report_id",
        string="Reports Including Documents",
        domain=[("model", "=", "purchase.order"), ("report_type", "like", "qweb-pdf")],
        default=lambda self: self._default_purchase_document_report_ids(),
        help="The PDF documents shared with the vendor are appended to these reports.",
    )
    purchase_bom_report_id = fields.Many2one(
        comodel_name="ir.actions.report",
        string="Subcontracting BoM Report",
        domain=[("model", "=", "mrp.bom"), ("report_type", "like", "qweb-pdf")],
        default=lambda self: self._default_purchase_bom_report_id(),
        help="Report used to generate the bill of materials sent to the subcontractors.",
    )

    @api.model
    def _default_purchase_document_report_ids(self):
        """Return the standard RFQ and purchase order reports.

        :return: ir.actions.report recordset
        """
        reports = self.env["ir.actions.report"]
        for xmlid in (
            "purchase.report_purchase_quotation",
            "purchase.action_report_purchase_order",
        ):
            reports |= self.env.ref(xmlid, raise_if_not_found=False) or reports
        return reports

    @api.model
    def _default_purchase_bom_report_id(self):
        """Return the subcontracting BoM report of this module.

        :return: ir.actions.report record (may be empty)
        """
        return self.env.ref(
            "s6r_purchase_product_document.action_report_purchase_bom",
            raise_if_not_found=False,
        ) or self.env["ir.actions.report"]
