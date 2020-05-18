from odoo import models, api, fields, _
from ast import literal_eval
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning
import logging

_logger = logging.getLogger(__name__)


class SaleViaticWizardLine(models.TransientModel):
    _name = 'sale.viatic.wizard.line'
    _description = 'Sale viatic Wizard Line'

    wizard_id = fields.Many2one('sale.viatic.wizard', string='Wizard')
    state = fields.Selection([('draft', 'Draft'), ('open', 'Open'), (
        'close', 'Close'), ('cancel', 'Cancel')], string='State', default='draft')
    line_id = fields.Many2one('sale.viatic.line', string='Line', readonly=True)
    sale_viatic_id = fields.Many2one(
        'sale.viatic', string='viatic', readonly=True)
    partner_id = fields.Many2one(
        "res.partner", string="Partner", readonly=True)
    product_id = fields.Many2one('product.product', domain=[
                                 ('viatic_ok', '=', True)], string='Product')
    cost = fields.Float(string='Cost', )
    markup = fields.Float(string='MarkUp', default=1.0)
    quantity = fields.Integer(string='Quantity', states={
                              'draft': [('readonly', False)]},)
    cost_total = fields.Integer(
        string='Cost Total', compute='_compute_price', readonly=True)
    price_unit = fields.Integer(
        string='Unit Price', compute='_compute_price', readonly=True)
    price_total = fields.Integer(
        string='Total Price', compute='_compute_price', readonly=True)

    @api.depends('quantity', 'cost', 'markup', 'state')
    def _compute_price(self):
        res = {}
        for line in self:
            cost = line.cost
            price_unit = line.cost * line.markup
            line.cost_total = round(cost * line.quantity, 2)
            line.price_unit = round(price_unit, 2)
            line.price_total = round(price_unit * line.quantity, 2)


class SaleViaticWizard(models.TransientModel):

    _name = 'sale.viatic.wizard'
    _description = 'Sale viatic Wizard'

    @api.model
    def _default_order(self):
        if self._context.get('active_ids'):
            return self._context.get('active_ids')[0]

    @api.model
    def _default_lines(self):
        _logger.debug('========get default lines====== %r',
                      self._context.get('active_ids'))
        sale_obj = self.env['sale.order']
        lines = []
        for sale in sale_obj.browse(self._context.get('active_ids')):
            if sale.viatic_ids:
                for viatic in sale.viatic_ids:
                    for line in viatic.line_ids:
                        lines.append({
                            'product_id': line.product_id.id,
                            'quantity': line.quantity,
                            'markup': 1.0,
                            'line_id': line.id,
                            'cost': line.cost,
                            'partner_id': line.sale_viatic_id.partner_id.id,
                            'sale_viatic_id': line.sale_viatic_id.id,
                            'state': line.sale_viatic_id.state})
        if len(lines) <= 0:
            product_obj = self.env['product.product']
            for product in product_obj.search([('viatic_ok', '=', True)]):
                _logger.debug('========get default line====== %r', product.id)
                lines.append({
                    'product_id': product.id,
                    'markup': 1.0,
                    'cost': product.standard_price or 0.0,
                    'cost_total': product.standard_price or 0.0,
                    'price_unit': product.standard_price or 0.0,
                    'price_total': product.standard_price or 0.0,
                    'quantity': 1.0})

        return lines

    line_ids = fields.One2many(
        'sale.viatic.wizard.line', 'wizard_id', string='Lines', default=_default_lines)
    order_id = fields.Many2one(
        "sale.order", string="Order", readonly=True, default=_default_order)

    @api.multi
    def set_viatic(self):
        line_obj = self.env['sale.viatic.line']
        viatic_obj = self.env['sale.viatic']
        lines = []
        must = False
        for wiz in self:
            for line in wiz.line_ids:
                if line.quantity > 0 and line.product_id:
                    must = True
            if must:

                open_viatic = False
                for line in wiz.line_ids:
                    if line.line_id and line.line_id.sale_viatic_id.state == 'draft':
                        open_viatic = line.line_id.sale_viatic_id

                for line in wiz.line_ids:
                    if line.line_id:
                        if line.line_id.sale_viatic_id and line.line_id.sale_viatic_id.state == 'draft':
                            line.line_id.quantity = line.quantity
                    else:
                        if line.product_id.id and line.quantity > 0:
                            if not open_viatic:
                                vals = {
                                    'sale_order_id': wiz.order_id.id,
                                    'partner_id': wiz.order_id.partner_id.id,
                                    'line_ids': False
                                }
                                open_viatic = viatic_obj.create(vals)

                            line_vals = {
                                'sale_viatic_id': open_viatic.id,
                                'product_id': line.product_id.id,
                                'quantity': line.quantity,
                                'markup': line.markup,
                                'cost': line.cost or 0.0,
                                'partner_id': wiz.order_id.partner_id.id
                            }
                            line_obj.create(line_vals)

                open_viatic.action_set()
                open_viatic.action_open()
