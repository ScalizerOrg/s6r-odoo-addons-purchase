# Copyright 2026 Scalizer (<https://www.scalizer.fr>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class ProductDocument(models.Model):
    _inherit = "product.document"

    attached_on_purchase = fields.Selection(
        selection=[
            ("hidden", "Hidden"),
            ("rfq", "On RFQ only"),
            ("rfq_purchase", "On RFQ and PO"),
            ("purchase", "On PO only"),
        ],
        string="Purchase: Visible at",
        required=True,
        default="hidden",
        help="Allows you to share the document with your vendors within a purchase.\n"
        "On RFQ only: available while the order is a request for quotation.\n"
        "On RFQ and PO: available at any time.\n"
        "On PO only: available once the order is confirmed.",
    )
