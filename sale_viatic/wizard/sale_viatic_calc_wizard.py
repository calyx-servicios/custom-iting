from odoo import models, api, fields, _
from ast import literal_eval
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning
import logging

_logger = logging.getLogger(__name__)


class SaleViaticCalcWizardLine(models.TransientModel):
    _name = 'sale.viatic.calc.wizard.line'
    _description = 'Sale viatic Calc Wizard Line'
   
    wizard_id = fields.Many2one('sale.viatic.calc.wizard', string='Wizard')
    
    sale_viatic_id = fields.Many2one('sale.viatic', string='viatic',readonly=True)
    viatic_id= fields.Integer('Viatic ID',readonly=True)
    net_profit= fields.Float('Net Profit',readonly=True)
    commission_percentage=fields.Float('Commission Percentage',)
    commission_amount= fields.Float('Comission Amount', compute='_compute_commission')
    commission_state = fields.Selection([('draft', 'Draft'),('paid', 'Paid'),('cancel', 'Cancel')], string='State',default='draft',readonly=True)

    @api.depends('commission_percentage','net_profit')
    def _compute_commission(self):
        res = {}
        for line in self:
            line.commission_amount=round(line.commission_percentage*line.net_profit/100.0,2)

    

class SaleViaticCalcWizard(models.TransientModel):

    _name = 'sale.viatic.calc.wizard'
    _description = 'Sale Viatic Calc Wizard'



    @api.model
    def _default_lines(self):
        _logger.debug('========get default lines====== %r', self._context.get('active_ids'))
        viatic_obj = self.env['sale.viatic']
        lines = []
        for viatic in viatic_obj.browse(self._context.get('active_ids')):
            lines.append({
                    'sale_viatic_id':viatic.id,
                    'viatic_id':viatic.id,
                    'net_profit': viatic.net_profit,
                    'commission_percentage': viatic.commission_percentage,
                    'commission_state': viatic.commission_state
                    })
        
        return lines

    line_ids = fields.One2many('sale.viatic.calc.wizard.line', 'wizard_id', string='Lines', default=_default_lines)
    


    @api.multi
    def set_viatic(self):
        viatic_obj = self.env['sale.viatic']
        for wiz in self:
            for viatic in wiz.line_ids:
                viatic_obj = self.env['sale.viatic']
                _viatic=viatic_obj.browse(viatic.viatic_id)
                _logger.debug('===>%r',_viatic.name)
                _viatic.commission_percentage=viatic.commission_percentage
        return {}        

    @api.multi
    def set_viatic_and_pay(self):
        viatic_obj = self.env['sale.viatic']
        for wiz in self:
            for viatic in wiz.line_ids:
                viatic_obj = self.env['sale.viatic']
                _viatic=viatic_obj.browse(viatic.viatic_id)
                _logger.debug('===>%r',_viatic.name)
                _viatic.commission_percentage=viatic.commission_percentage
                _viatic.commission_state='paid'
        return {}                      
        
        
                
    
    

