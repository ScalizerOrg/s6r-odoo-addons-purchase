# Copyright 2026 Scalizer (<https://www.scalizer.fr>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    purchase_document_report_ids = fields.Many2many(
        related="company_id.purchase_document_report_ids",
        readonly=False,
    )
    purchase_bom_report_id = fields.Many2one(
        related="company_id.purchase_bom_report_id",
        readonly=False,
    )
