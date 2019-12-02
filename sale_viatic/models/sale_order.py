# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, api, fields, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    viatic_ids = fields.One2many('sale.viatic', 'sale_order_id', string='Viatic Lines',)
    amount_cost = fields.Monetary(compute='_sale_cost', help="It gives total cost.", currency_field='currency_id', digits=dp.get_precision('Product Price'), store=True)

    @api.depends('order_line.cost','order_line.product_id', 'order_line.purchase_price', 'order_line.product_uom_qty','order_line')
    def _sale_cost(self):
        for order in self:
            order.amount_cost = sum(order.order_line.filtered(lambda r: r.state != 'cancel').mapped('cost'))


    def set_viatics(self):
            return {    
                'name': _("Viatics"),
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'sale.viatic.wizard',
                'target': 'new',
                
            }
        
 

class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    cost = fields.Float(compute='_product_cost', digits=dp.get_precision('Product Price'), store=True)
    

    @api.depends('product_id', 'purchase_price', 'product_uom_qty')
    def _product_cost(self):
        for line in self:
            currency = line.order_id.pricelist_id.currency_id
            price = line.purchase_price
            line.cost =  price * line.product_uom_qty


