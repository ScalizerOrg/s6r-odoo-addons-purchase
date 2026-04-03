# Copyright 2026 Scalizer (<https://www.scalizer.fr>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from odoo import api


def post_init_hook(env):
    env = api.Environment(env.cr, env.uid, {})

    group = env.ref(
        "s6r_purchase_my_documents_only.group_purchase_my_documents_only",
        raise_if_not_found=False,
    )
    if not group:
        return

    DashboardGroup = env["spreadsheet.dashboard.group"].sudo()
    Lang = env["res.lang"].sudo()

    dashboard_group_id = DashboardGroup.create({"name": "Purchase"})

    fr_lang = Lang.search([("code", "=", "fr_FR")], limit=1)
    if fr_lang:
        dashboard_group_id.with_context(lang="fr_FR").write({
            "name": "Achat",
        })

    dashboard_id = env.ref(
        "spreadsheet_dashboard_purchase_stock.spreadsheet_dashboard_purchase").sudo()

    dashboard_id.write({
        "dashboard_group_id": dashboard_group_id.id,
        "group_ids": [(6, 0, [group.id])]
    })
