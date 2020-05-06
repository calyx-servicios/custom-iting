from odoo import models, api, fields, _
from ast import literal_eval
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning
import logging

_logger = logging.getLogger(__name__)


class SaleViaticCalcWizardLine(models.TransientModel):
    _name = 'sale.viatic.calc.wizard.line'
    _description = 'Sale viatic Calc Wizard Line'

    wizard_id = fields.Many2one('sale.viatic.calc.wizard', string='Wizard')

    sale_viatic_id = fields.Many2one(
        'sale.viatic', string='viatic', readonly=True)
    viatic_id = fields.Integer('Viatic ID', readonly=True)
    net_profit = fields.Float('Net Profit', readonly=True)
    commission_percentage = fields.Float('Commission Percentage',)
    commission_amount = fields.Float(
        'Comission Amount', compute='_compute_commission')
    commission_state = fields.Selection([('draft', 'Draft'), ('paid', 'Paid'), (
        'cancel', 'Cancel')], string='State', default='draft', readonly=True)
    state = fields.Selection(
        [('payable', 'Payable'), ('unpayable', 'Unpayable')], readonly=True)

    @api.depends('commission_percentage', 'net_profit')
    def _compute_commission(self):
        res = {}
        for line in self:
            line.commission_amount = round(
                line.commission_percentage * line.net_profit / 100.0, 2)


class SaleViaticCalcWizard(models.TransientModel):

    _name = 'sale.viatic.calc.wizard'
    _description = 'Sale Viatic Calc Wizard'

    @api.model
    def _default_lines(self):
        _logger.debug('========get default lines====== %r',
                      self._context.get('active_ids'))
        #viatic_obj = self.env['sale.viatic']
        lines = []
        # vitatics = []
        # for so in self.env['sale.order'].browse(self._context.get('active_ids')):
        #     vitatics.add 
        for order in self.env['sale.order'].browse(self._context.get('active_ids')):
            full_paid = False
            for viatic in order.viatic_ids:
                if viatic.invoice_ids and len(viatic.invoice_ids) > 0:
                    full_paid = True
                for invoice in viatic.invoice_ids:
                    if invoice.state not in ['paid', 'open', 'draft']:
                        full_paid = False
                state = 'unpayable'
                if order.invoice_state in ['paid']:
                    state = 'payable'
                if full_paid:
                    lines.append({
                        'sale_viatic_id': viatic.id,
                        'viatic_id': viatic.id,
                        'net_profit': order.net_profit,
                        'commission_percentage': order.commission_percentage,
                        'commission_state': order.commission_state,
                        'commission_amount': order.commission_amount,
                        'state': state
                    })
        if len(lines) > 0:
            return lines
        else:
            raise UserError(
                _('Please Select Viatics of Invoiced and Paid Sales Orders!'))

    line_ids = fields.One2many(
        'sale.viatic.calc.wizard.line', 'wizard_id', string='Lines', default=_default_lines)

    commission_amount = fields.Float(
        'Comission Amount', compute='_compute_commission')

    @api.depends('line_ids.commission_percentage')
    def _compute_commission(self):
        res = {}
        total = 0.0
        for line in self.line_ids:
            total += line.commission_amount
        self.commission_amount = round(total, 2)

    @api.multi
    def set_viatic(self):
        viatic_obj = self.env['sale.viatic']
        for wiz in self:
            for viatic in wiz.line_ids:
                _viatic = viatic_obj.browse(viatic.viatic_id)
                _logger.debug('===>%r', _viatic.name)
                _viatic.sale_order_id.commission_percentage = viatic.commission_percentage
        return {}

    @api.multi
    def set_viatic_and_pay(self):
        viatic_obj = self.env['sale.viatic']
        for wiz in self:
            for viatic in wiz.line_ids:
                viatic_obj = self.env['sale.viatic']
                _viatic = viatic_obj.browse(viatic.viatic_id)
                _logger.debug('===>%r', _viatic.name)
                _viatic.sale_order_id.commission_percentage = viatic.commission_percentage
                if _viatic.sale_order_id.invoice_state in ['paid']:
                    _viatic.sale_order_id.commission_state = 'paid'
        return {}
