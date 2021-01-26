# Copyright 2020 Calyx Servicios S.A
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models, fields


class AccountAnalyticContractLine(models.Model):
    _inherit = "account.analytic.contract.line"

    purchase_price = fields.Float(string="Purchase Price")
