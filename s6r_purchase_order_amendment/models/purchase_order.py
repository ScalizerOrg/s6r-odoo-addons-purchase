# Copyright 2026 Scalizer (<https://www.scalizer.fr>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from odoo import _, api, fields, models
from odoo.exceptions import UserError

AMENDMENT_SUFFIX_FORMAT = "AMDT-%02d"


class PurchaseOrder(models.Model):
    """Extend purchase.order to track amendments (avenants).

    An amendment is a regular purchase order duplicated from an origin
    order, used to cover the gap when a vendor bill amount exceeds the
    remaining amount to invoice on the origin order. This module only
    tracks the link between the origin order and its amendment(s); it
    does not compute the invoicing gap nor trigger the amendment
    creation automatically.
    """

    _inherit = "purchase.order"

    amendment_of_id = fields.Many2one(
        comodel_name="purchase.order",
        string="Amendment Of",
        copy=False,
        readonly=True,
        index=True,
        help="Origin purchase order this order is an amendment of.",
    )
    amendment_ids = fields.One2many(
        comodel_name="purchase.order",
        inverse_name="amendment_of_id",
        string="Amendments",
        copy=False,
        readonly=True,
    )
    amendment_count = fields.Integer(
        string="Amendment Count",
        compute="_compute_amendment_count",
    )

    @api.depends("amendment_ids")
    def _compute_amendment_count(self):
        """Compute the number of amendments linked to this order.

        :return: None, sets ``amendment_count`` on each record in ``self``
        """
        for order in self:
            order.amendment_count = len(order.amendment_ids)

    @api.constrains("amendment_of_id")
    def _check_amendment_of_id(self):
        """Prevent an order from being its own amendment.

        :raises UserError: if ``amendment_of_id`` points to the record itself
        """
        for order in self:
            if order.amendment_of_id == order:
                raise UserError(_("A purchase order cannot be an amendment of itself."))

    def action_create_amendment(self):
        """Duplicate the current order as a new amendment.

        Only available on a confirmed order (``state == 'purchase'``) that
        is not itself an amendment. The new order is a copy of ``self``
        with ``amendment_of_id`` set, and its name is rewritten as
        ``{origin_name}/AMDT-XX`` where XX is the next available index
        based on the number of existing amendments of the origin order.

        :raises UserError: if the order is not confirmed or is itself an amendment
        :return: an ir.actions.act_window opening the newly created amendment
        :rtype: dict
        """
        self.ensure_one()
        if self.state != "purchase" or self.amendment_of_id:
            raise UserError(_("An amendment can only be created from a confirmed purchase order that is not itself an amendment."))

        next_index = len(self.amendment_ids) + 1
        origin_name = self.name
        amendment = self.copy({"amendment_of_id": self.id})
        amendment.name = f"{origin_name}/{AMENDMENT_SUFFIX_FORMAT % next_index}"

        return {
            "type": "ir.actions.act_window",
            "res_model": "purchase.order",
            "view_mode": "form",
            "res_id": amendment.id,
        }

    def action_view_amendments(self):
        """Open the amendments linked to this order.

        Opens the list view if there is more than one amendment, or the
        form view directly if there is exactly one.

        :return: an ir.actions.act_window on the linked amendments
        :rtype: dict
        """
        self.ensure_one()
        action = {
            "type": "ir.actions.act_window",
            "name": _("Amendments"),
            "res_model": "purchase.order",
            "domain": [("amendment_of_id", "=", self.id)],
        }
        if self.amendment_count == 1:
            action.update(
                {
                    "view_mode": "form",
                    "res_id": self.amendment_ids.id,
                }
            )
        else:
            action["view_mode"] = "list,form"
        return action
