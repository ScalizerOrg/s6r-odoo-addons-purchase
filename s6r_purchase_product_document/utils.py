# Copyright 2025 Scalizer (<https://www.scalizer.fr>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0.html).
import io

from odoo import _
from odoo.exceptions import ValidationError
from odoo.tools import pdf


def _ensure_document_not_encrypted(document):
    if pdf.PdfFileReader(io.BytesIO(document), strict=False).isEncrypted:
        raise ValidationError(_(
            "It seems that we're not able to process this pdf inside a purchase order. It is either "
            "encrypted, or encoded in a format we do not support."
        ))
