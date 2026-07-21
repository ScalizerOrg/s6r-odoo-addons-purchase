# Copyright 2026 Scalizer (<https://www.scalizer.fr>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0.html).
{
    "name": "Scalizer Purchase Order Report Product Image",
    "version": "19.0.0.0.0",
    "author": "Scalizer",
    "website": "https://www.scalizer.fr",
    "summary": "Show product images on Purchase documents",
    "sequence": 0,
    "license": "AGPL-3",
    "depends": ["purchase"],
    "category": "Generic Modules/Scalizer",
    "complexity": "easy",
    "qweb": [],
    "demo": [],
    "images": [],
    "data": [
        "views/report_purchaseorder.xml",
        "views/report_purchasequotation.xml",
    ],
    "auto_install": False,
    "installable": True,
    "application": False,
}
