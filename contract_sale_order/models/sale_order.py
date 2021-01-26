# Copyright 2020 Calyx Servicios S.A
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models, fields


class SaleOrder(models.Model):
    _inherit = "sale.order"

    contract_id = fields.Many2one(
        "account.analytic.account", string="Contract"
    )
