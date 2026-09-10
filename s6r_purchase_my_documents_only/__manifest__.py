# Copyright 2026 Scalizer (<https://www.scalizer.fr>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
{
    "name": "Scalizer Purchase - My Documents Only",
    "version": "19.0.1.0.1",
    "summary": "Restrict purchase users to their own purchase documents and related vendor bills",
    "category": "Purchases",
    "author": "Scalizer",
    "website": "https://www.scalizer.fr",
    "license": "LGPL-3",
    "depends": [
        "account",
        "purchase_requisition",
    ],
    "data": [
        "security/purchase_my_documents_groups.xml",
        "security/ir.model.access.csv",
        "security/purchase_my_documents_rules.xml",
        "views/purchase_menu_views.xml",
    ],
    "post_init_hook": "post_init_hook",
    "installable": True,
    "application": False,
}
