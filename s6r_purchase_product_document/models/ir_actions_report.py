# Copyright 2026 Scalizer (<https://www.scalizer.fr>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

import io
import logging

from odoo import api, models
from odoo.tools.pdf import OdooPdfFileReader, OdooPdfFileWriter

_logger = logging.getLogger(__name__)


class IrActionsReport(models.Model):
    _inherit = "ir.actions.report"

    def _render_qweb_pdf_prepare_streams(self, report_ref, data, res_ids=None):
        """Append the PDF documents shared with the vendor to the order report."""
        result = super()._render_qweb_pdf_prepare_streams(report_ref, data, res_ids=res_ids)
        report = self._get_report(report_ref)
        if report.model != "purchase.order" or not res_ids:
            return result
        for order in self.env["purchase.order"].browse(res_ids).sudo():
            stream = result.get(order.id, {}).get("stream")
            if not stream or report not in order.company_id.purchase_document_report_ids:
                continue
            contents = order._get_purchase_pdf_contents()
            if contents:
                result[order.id]["stream"] = self._append_pdf_contents(stream, contents)
        return result

    @api.model
    def _append_pdf_contents(self, stream, contents):
        """Append PDF files to a PDF stream.

        The files embedded in the main PDF (e.g. the EDI documents of the
        purchase order) are embedded again in the new PDF. A file which can
        not be read is skipped.

        :param stream: io.BytesIO of the main PDF
        :param contents: list of PDF contents (bytes) to append
        :return: new io.BytesIO
        """
        reader = OdooPdfFileReader(io.BytesIO(stream.getvalue()), strict=False)
        writer = OdooPdfFileWriter()
        writer.append_pages_from_reader(reader)
        for content in contents:
            try:
                document_reader = OdooPdfFileReader(io.BytesIO(content), strict=False)
                pages = list(document_reader.pages)
            except Exception:  # pylint: disable=broad-except
                _logger.warning("A document could not be appended to the PDF", exc_info=True)
                continue
            for page in pages:
                writer.add_page(page)
        for name, data in reader.get_attachments():
            subtype = "text/xml" if str(name).lower().endswith(".xml") else None
            writer.add_attachment(str(name), data, subtype=subtype)
        new_stream = io.BytesIO()
        writer.write(new_stream)
        stream.close()
        return new_stream
