# Copyright 2026 Scalizer (<https://www.scalizer.fr>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    "name": "Scalizer Purchase Product Document",
    "version": "20.0.1.0.0",
    "author": "Scalizer",
    "website": "https://www.scalizer.fr",
    "category": "Generic Modules/Scalizer",
    "summary": "Share product documents and subcontracting BoMs with vendors "
    "on RFQs and purchase orders",
    "sequence": 0,
    "license": "LGPL-3",
    "depends": [
        "mrp_subcontracting_purchase",
        "project_mrp",
        "project_purchase",
    ],
    "complexity": "easy",
    "description": """
Share product documents with vendors on RFQs and purchase orders:
- visibility of each product document on RFQs and/or purchase orders;
- selection of the documents to send on the purchase order;
- PDF of the subcontracting bill of materials, frozen at confirmation;
- PDF documents appended to the RFQ / purchase order report;
- download links and zipped non-PDF documents in the email;
- documents section on the vendor portal.
    """,
    "qweb": [],
    "demo": [],
    "images": ["static/description/icon.png"],
    "data": [
        # Security
        "security/ir.access.csv",
        # Reports
        "report/purchase_bom_report.xml",
        # Views
        "views/product_document_views.xml",
        "views/purchase_order_document_views.xml",
        "views/purchase_order_views.xml",
        "views/purchase_portal_templates.xml",
        "views/mail_templates.xml",
        "views/res_config_settings_views.xml",
    ],
    "post_init_hook": "post_init_hook",
    "auto_install": False,
    "installable": True,
    "application": False,
}
