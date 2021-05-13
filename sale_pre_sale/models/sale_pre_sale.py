from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    pre_sale = fields.Many2many(
        string = 'Pre-sale',
        comodel_name = 'res.users',
        required = True
    )