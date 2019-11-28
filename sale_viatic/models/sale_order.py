from odoo import models, api, fields, _
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    

    viatic_ids = fields.One2many('sale.viatic', 'sale_order_id', string='Viatic Lines',)



    def set_viatics(self):
        
                
            return {    
                'name': _("Viatics"),
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'sale.viatic.wizard',
                'target': 'new',
                
            }
        
    