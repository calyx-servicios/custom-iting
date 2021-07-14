from odoo import models, fields, api

class ResUsers(models.Model):
    _inherit= "res.users"

    is_pre_sale = fields.Boolean(string = "Is Pre-Sale")

    