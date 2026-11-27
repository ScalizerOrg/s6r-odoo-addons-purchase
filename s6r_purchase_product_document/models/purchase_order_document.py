# Copyright 2026 Scalizer (<https://www.scalizer.fr>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class PurchaseOrderDocument(models.Model):
    _name = "purchase.order.document"
    _description = "Purchase Order Document"
    _order = "order_id, sequence, id"

    order_id = fields.Many2one(
        comodel_name="purchase.order",
        string="Purchase Order",
        required=True,
        index=True,
        ondelete="cascade",
    )
    company_id = fields.Many2one(related="order_id.company_id", store=True)
    sequence = fields.Integer(default=10)
    available_product_document_ids = fields.Many2many(
        related="order_id.available_product_document_ids",
    )
    product_document_id = fields.Many2one(
        comodel_name="product.document",
        string="Document",
        required=True,
        index=True,
        ondelete="cascade",
        domain="[('id', 'in', available_product_document_ids)]",
    )
    attached_on_purchase = fields.Selection(
        related="product_document_id.attached_on_purchase",
    )
    mimetype = fields.Char(related="product_document_id.mimetype")
    product_name = fields.Char(
        string="Product",
        related="product_document_id.res_name",
    )

    _unique_document = models.Constraint(
        "UNIQUE(order_id, product_document_id)",
        "This document is already selected on the purchase order.",
    )
