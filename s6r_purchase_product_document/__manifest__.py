# Copyright 2025 Scalizer (<https://www.scalizer.fr>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
{
    'name': 'Scalizer Purchase Product Document',
    'version': '17.0.1.0.0',
    'author': 'Scalizer',
    'website': 'https://www.scalizer.fr',
    'summary': "Add product PDFs to purchase orders and RFQs",
    'sequence': 0,
    'license': 'LGPL-3',
    'depends': [
        'purchase',
    ],
    'category': 'Generic Modules/Scalizer',
    'complexity': 'easy',
    'description': '''
This module allows adding PDFs from product documents to purchase orders and RFQs.
    ''',
    'data': [
        # Views
        'views/product_document_views.xml',
    ],
    'auto_install': False,
    'installable': True,
    'application': False,
}
