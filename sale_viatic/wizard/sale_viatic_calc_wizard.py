from odoo import models, api, fields, _
from ast import literal_eval
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning
import logging

_logger = logging.getLogger(__name__)


class SaleViaticCalcWizardLine(models.TransientModel):
    _name = 'sale.viatic.calc.wizard.line'
    _description = 'Sale viatic Calc Wizard Line'

    wizard_id = fields.Many2one('sale.viatic.calc.wizard', string='Wizard')

    sale_order_id = fields.Many2one(
        'sale.order', string='Sale Order', readonly=True)
    order_id = fields.Integer()
    salesman_id = fields.Many2one(
        related='sale_order_id.user_id', store=True, string='Salesperson', readonly=True)
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
        lines = []
        for order in self.env['sale.order'].browse(self._context.get('active_ids')):
            full_paid = False
            order.set_commisions()
            state = 'payable'
            if order.invoice_ids and len(order.invoice_ids) > 0:
                full_paid = True
            for invoice in order.invoice_ids:
                if invoice.state not in ['paid', 'open', 'draft']:
                    full_paid = False
                if invoice.state not in ['paid']:
                    state = 'unpayable'
            if order.commission_ids[0].commission_state in ['paid'] or order.amount_cost ==0.0:
                state = 'unpayable'
            if full_paid:
                lines.append({
                    'sale_order_id': order.id,
                    'order_id': order.id,
                    'user_id': order.commission_ids[0].salesman_id,
                    'net_profit': order.net_profit,
                    'commission_percentage': order.commission_ids[0].commission_percentage,
                    'commission_state': order.commission_ids[0].commission_state,
                    'commission_amount': order.commission_ids[0].commission_amount,
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
    def set_commission(self):
        order_obj = self.env['sale.order']
        for line in self.line_ids:
            order = order_obj.browse(line.order_id)
            state = 'payable'
            for invoice in order.invoice_ids:
                if invoice.state not in ['paid']:
                    state = 'unpayable'
            if state in ['payable']:
                order.commission_ids[
                    0].commission_percentage = line.commission_percentage
        return {}

    @api.multi
    def set_commission_and_pay(self):
        order_obj = self.env['sale.order']
        for line in self.line_ids:
            order = order_obj.browse(line.order_id)
            state = 'payable'
            for invoice in order.invoice_ids:
                if invoice.state not in ['paid']:
                    state = 'unpayable'
            if state in ['payable']:
                order.commission_ids[0].commission_state = 'paid'
                order.commission_ids[
                    0].commission_percentage = line.commission_percentage
        return {}
