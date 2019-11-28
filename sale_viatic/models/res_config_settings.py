# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from ast import literal_eval

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    viatic_product=fields.Many2one('product.product', string='Viatic Product', domain=[('sale_ok', '=', True)])
    viatic_fee=fields.Float('Fee',help='Default Fee for Viatics')
    viatic_tax=fields.Float('Tax',help='Default Tax for Viatics')

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        ICPSudo = self.env['ir.config_parameter'].sudo()
        viatic_product_id = literal_eval(ICPSudo.get_param('sale_viatic.viatic_product', default='False'))
        if viatic_product_id and not self.env['product.product'].browse(viatic_product_id).exists():
            viatic_product_id = False
        res.update(
            viatic_product=viatic_product_id,
            viatic_fee=float(ICPSudo.get_param('sale_viatic.viatic_fee') or 0.0),
            viatic_tax=float(ICPSudo.get_param('sale_viatic.viatic_tax') or 0.0)
        )
        return res

    @api.multi
    def set_values(self):
        super(ResConfigSettings, self).set_values()
        ICPSudo = self.env['ir.config_parameter'].sudo()
        ICPSudo.set_param("sale_viatic.viatic_product", self.viatic_product.id)
        ICPSudo.set_param("sale_viatic.viatic_fee", self.viatic_fee)
        ICPSudo.set_param("sale_viatic.viatic_tax", self.viatic_tax)