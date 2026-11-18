# Copyright 2026 Scalizer (<https://www.scalizer.fr>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

import io
import zipfile

from PIL import Image

from odoo.tests import HttpCase, TransactionCase, tagged
from odoo.tools.pdf import OdooPdfFileReader, PdfFileWriter


def make_pdf(pages=1):
    """Return the content of a blank PDF.

    :param pages: number of pages
    :return: bytes
    """
    writer = PdfFileWriter()
    for _index in range(pages):
        writer.add_blank_page(width=200, height=200)
    buffer = io.BytesIO()
    writer.write(buffer)
    return buffer.getvalue()


def make_png():
    """Return the content of a 1 pixel PNG image.

    :return: bytes
    """
    buffer = io.BytesIO()
    Image.new("RGB", (1, 1)).save(buffer, format="PNG")
    return buffer.getvalue()


class PurchaseProductDocumentCommon(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.vendor = cls.env["res.partner"].create({"name": "Vendor", "email": "vendor@example.com"})
        cls.project = cls.env["project.project"].create({"name": "Project"})
        cls.product = cls.env["product.product"].create({"name": "Purchased Product", "type": "consu"})
        cls.subcontracted = cls.env["product.product"].create(
            {"name": "Subcontracted Product", "type": "consu"}
        )
        cls.component = cls.env["product.product"].create({"name": "Component", "type": "consu"})
        cls.bom = cls._create_bom()
        cls.pdf_content = make_pdf(2)
        Document = cls.env["product.document"]
        cls.doc_pdf = Document.create(
            {
                "name": "plan.pdf",
                "raw": cls.pdf_content,
                "res_model": "product.template",
                "res_id": cls.product.product_tmpl_id.id,
                "attached_on_purchase": "rfq_purchase",
            }
        )
        cls.doc_png = Document.create(
            {
                "name": "picture.png",
                "raw": make_png(),
                "res_model": "product.product",
                "res_id": cls.product.id,
                "attached_on_purchase": "rfq",
            }
        )
        cls.doc_po = Document.create(
            {
                "name": "certificate.pdf",
                "raw": make_pdf(),
                "res_model": "product.template",
                "res_id": cls.product.product_tmpl_id.id,
                "attached_on_purchase": "purchase",
            }
        )
        cls.doc_hidden = Document.create(
            {
                "name": "internal.pdf",
                "raw": make_pdf(),
                "res_model": "product.template",
                "res_id": cls.product.product_tmpl_id.id,
            }
        )

    @classmethod
    def _create_bom(cls, project=None):
        return cls.env["mrp.bom"].create(
            {
                "product_tmpl_id": cls.subcontracted.product_tmpl_id.id,
                "type": "subcontract",
                "subcontractor_ids": [(6, 0, cls.vendor.ids)],
                "project_id": project and project.id,
                "bom_line_ids": [(0, 0, {"product_id": cls.component.id, "product_qty": 2})],
            }
        )

    def _create_order(self, products, project=None):
        return self.env["purchase.order"].create(
            {
                "partner_id": self.vendor.id,
                "project_id": project and project.id,
                "order_line": [
                    (0, 0, {"product_id": product.id, "product_qty": 1, "price_unit": 10})
                    for product in products
                ],
            }
        )

    def _select_documents(self, order, documents):
        order.document_ids = [
            (0, 0, {"product_document_id": document.id, "sequence": sequence})
            for sequence, document in enumerate(documents)
        ]


@tagged("post_install", "-at_install")
class TestPurchaseProductDocument(PurchaseProductDocumentCommon):
    def test_default_visibility(self):
        self.assertEqual(self.doc_hidden.attached_on_purchase, "hidden")

    def test_available_documents(self):
        order = self._create_order(self.product)
        self.assertEqual(
            set(order.available_product_document_ids.ids),
            {self.doc_pdf.id, self.doc_png.id, self.doc_po.id},
        )

    def test_shared_documents_by_state(self):
        order = self._create_order(self.product)
        self._select_documents(order, self.doc_png | self.doc_po | self.doc_pdf)
        self.assertEqual(order.document_count, 3)
        self.assertEqual(order._get_purchase_documents().ids, [self.doc_png.id, self.doc_pdf.id])
        order.button_confirm()
        self.assertEqual(order._get_purchase_documents().ids, [self.doc_po.id, self.doc_pdf.id])
        self.doc_pdf.active = False
        self.assertEqual(order._get_purchase_documents(), self.doc_po)

    def test_bom_single_candidate(self):
        order = self._create_order(self.product | self.subcontracted)
        line_product, line_subcontracted = order.order_line
        self.assertFalse(line_product.is_subcontracted)
        self.assertFalse(line_product.bom_id)
        self.assertTrue(line_subcontracted.is_subcontracted)
        self.assertEqual(line_subcontracted.bom_id, self.bom)

    def test_bom_several_candidates(self):
        other_bom = self._create_bom()
        order = self._create_order(self.subcontracted)
        self.assertEqual(order.order_line.available_bom_ids, self.bom | other_bom)
        self.assertFalse(order.order_line.bom_id)

    def test_bom_project(self):
        other_project = self.env["project.project"].create({"name": "Other Project"})
        project_bom = self._create_bom(self.project)
        self._create_bom(other_project)
        order = self._create_order(self.subcontracted)
        self.assertEqual(order.order_line.bom_id, self.bom)
        order = self._create_order(self.subcontracted, self.project)
        self.assertEqual(order.order_line.available_bom_ids, self.bom | project_bom)
        self.assertFalse(order.order_line.bom_id)

    def test_freeze_bom_pdf(self):
        order = self._create_order(self.subcontracted)
        line = order.order_line
        self.assertFalse(line.bom_attachment_id)
        order.button_confirm()
        attachment = line.bom_attachment_id
        self.assertTrue(attachment)
        self.assertEqual((attachment.res_model, attachment.res_id), ("purchase.order", order.id))
        self.assertEqual(line._get_bom_pdf(), (attachment.name, attachment.raw.content))
        order.button_cancel()
        order.button_draft()
        self.assertFalse(line.bom_attachment_id)
        self.assertFalse(attachment.exists())

    def test_append_pdf_contents(self):
        stream = io.BytesIO(make_pdf())
        with self.assertLogs(
            "odoo.addons.s6r_purchase_product_document.models.ir_actions_report", level="WARNING"
        ):
            new_stream = self.env["ir.actions.report"]._append_pdf_contents(
                stream, [self.pdf_content, b"not a pdf"]
            )
        reader = OdooPdfFileReader(io.BytesIO(new_stream.getvalue()), strict=False)
        self.assertEqual(len(reader.pages), 3)

    def test_email_attachments(self):
        order = self._create_order(self.product | self.subcontracted)
        self._select_documents(order, self.doc_pdf | self.doc_png)
        report = self.env.ref("purchase.report_purchase_quotation")

        files = dict(order._get_purchase_document_attachments(report))
        self.assertEqual(len(files), 1)
        zip_name = next(iter(files))
        self.assertTrue(zip_name.endswith(".zip"))
        with zipfile.ZipFile(io.BytesIO(files[zip_name])) as archive:
            self.assertEqual(archive.namelist(), ["picture.png"])

        order.company_id.purchase_document_report_ids = False
        files = dict(order._get_purchase_document_attachments(report))
        self.assertEqual(len(files), 3)
        self.assertEqual(files["plan.pdf"], self.pdf_content)
        self.assertIn("%s.pdf" % self.bom.display_name, files)

    def test_mail_composer(self):
        order = self._create_order(self.product)
        self._select_documents(order, self.doc_pdf | self.doc_png)
        action = order.with_context(send_rfq=True).action_rfq_send()
        composer = self.env["mail.compose.message"].with_context(**action["context"]).create({})
        self.assertIn(
            "%s - Documents.zip" % order.name.replace("/", "_"),
            composer.attachment_ids.mapped("name"),
        )
        self.assertIn("/document/%s" % self.doc_pdf.id, str(composer.body))
        self.assertIn("/document/%s" % self.doc_png.id, str(composer.body))

        composer = self.env["mail.compose.message"].with_context(
            **dict(action["context"], purchase_product_documents=False)
        ).create({})
        self.assertNotIn("/document/", str(composer.body))

    def test_preview(self):
        order = self._create_order(self.product)
        self.assertEqual(order.action_preview_purchase_order()["url"], order.get_portal_url())


@tagged("post_install", "-at_install")
class TestPurchaseProductDocumentPortal(HttpCase, PurchaseProductDocumentCommon):
    def test_portal_document_download(self):
        order = self._create_order(self.product)
        self._select_documents(order, self.doc_pdf | self.doc_po)

        response = self.url_open(order.get_portal_url("/document/%s" % self.doc_pdf.id))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, self.pdf_content)

        # Not shared on a RFQ / not selected / wrong access token
        for url in (
            order.get_portal_url("/document/%s" % self.doc_po.id),
            order.get_portal_url("/document/%s" % self.doc_hidden.id),
            "/my/purchase/%s/document/%s?access_token=wrong" % (order.id, self.doc_pdf.id),
        ):
            response = self.url_open(url)
            self.assertNotEqual(response.content, self.pdf_content)
            self.assertNotIn("/document/", response.url)

    def test_portal_page(self):
        order = self._create_order(self.product)
        self._select_documents(order, self.doc_pdf)
        response = self.url_open(order.get_portal_url())
        self.assertEqual(response.status_code, 200)
        self.assertIn("/document/%s" % self.doc_pdf.id, response.text)
