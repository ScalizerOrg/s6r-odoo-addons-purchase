# Copyright 2025 Scalizer (<https://www.scalizer.fr>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0.html).
import base64

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

from .. import utils


class ProductDocument(models.Model):
    _inherit = 'product.document'

    attached_on_purchase = fields.Selection(
        selection=[('inside', "Inside")],
        help="Allows you to share the document with your vendor within a purchase order.\n"
             "Leave it empty if you don't want to share this document with the vendor.\n"
             "Inside: The document will be included in the pdf after the RFQ or purchase \n"
             "order.\n"
    )

    @api.constrains('attached_on_purchase', 'datas', 'type')
    def _check_attached_on_purchase_and_datas_compatibility(self):
        for doc in self.filtered(lambda doc: doc.attached_on_purchase == 'inside'):
            if doc.type != 'binary':
                raise ValidationError(_(
                    "When attached inside a purchase, the document must be a file, not a URL."
                ))
            if doc.datas and not doc.mimetype.endswith('pdf'):
                raise ValidationError(_("Only PDF documents can be attached inside a purchase."))
            utils._ensure_document_not_encrypted(base64.b64decode(doc.datas))
