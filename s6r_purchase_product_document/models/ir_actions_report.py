# Copyright 2025 Scalizer (<https://www.scalizer.fr>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0.html).
import base64
import io

from odoo import models
from odoo.tools.pdf import PdfFileWriter, PdfFileReader


class IrActionsReport(models.Model):
    _inherit = 'ir.actions.report'

    def _render_qweb_pdf_prepare_streams(self, report_ref, data, res_ids=None):
        result = super()._render_qweb_pdf_prepare_streams(report_ref, data, res_ids=res_ids)
        if self._get_report(report_ref).report_name not in ['purchase.report_purchasequotation',
                                                            'purchase.report_purchaseorder']:
            return result

        orders = self.env['purchase.order'].browse(res_ids)

        for order in orders:
            initial_stream = result[order.id]['stream']
            if initial_stream:
                included_product_docs = self.env['product.document']
                for line in order.order_line:
                    product_product_docs = line.product_id.product_document_ids
                    product_template_docs = line.product_id.product_tmpl_id.product_document_ids
                    doc_to_include = (
                        product_product_docs.filtered(lambda d: d.attached_on_purchase == 'inside')
                        or product_template_docs.filtered(lambda d: d.attached_on_purchase == 'inside')
                    )
                    included_product_docs = included_product_docs | doc_to_include

                if not included_product_docs:
                    continue

                writer = PdfFileWriter()
                self._add_pages_to_writer(writer, initial_stream.getvalue())
                for doc in included_product_docs:
                    self._add_pages_to_writer(writer, base64.b64decode(doc.datas))

                with io.BytesIO() as _buffer:
                    writer.write(_buffer)
                    stream = io.BytesIO(_buffer.getvalue())
                result[order.id].update({'stream': stream})

        return result

    def _add_pages_to_writer(self, writer, document):
        reader = PdfFileReader(io.BytesIO(document), strict=False)
        for page_id in range(reader.getNumPages()):
            page = reader.getPage(page_id)
            writer.addPage(page)
