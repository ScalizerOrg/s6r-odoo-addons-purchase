# Copyright 2026 Scalizer (<https://www.scalizer.fr>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).


def post_init_hook(env):
    """Initialize the purchase document settings of the existing companies.

    :param env: Odoo environment
    """
    companies = env["res.company"].search([])
    companies.write(
        {
            "purchase_document_report_ids": [
                (6, 0, companies._default_purchase_document_report_ids().ids)
            ],
            "purchase_bom_report_id": companies._default_purchase_bom_report_id().id,
        }
    )
