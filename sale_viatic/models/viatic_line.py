from odoo import models, api, fields, _
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning
from ast import literal_eval
import logging

_logger = logging.getLogger(__name__)


class SaleViaticLine(models.Model):
    _name = 'sale.viatic.line'
    _description = 'Sales Viatic Line'

    @api.model
    def create(self, vals):
        if vals.get('quantity', 0) <= 0:
            raise ValidationError(_('Quantity Must be Positive'))
        return super(SaleViaticLine, self).create(vals)

    @api.model
    def write(self, vals):
        if vals.get('quantity') and vals.get('quantity') <= 0:
            raise ValidationError(_('Quantity Must be Positive'))
        return super(SaleViaticLine, self).write(vals)

    sale_viatic_id = fields.Many2one(
        'sale.viatic', string='Sale Viatic', ondelete='cascade')
    product_id = fields.Many2one('product.product', string='Product', domain=[(
        'viatic_ok', '=', True)], change_default=True, ondelete='restrict', required=True, states={'draft': [('readonly', False)]})
    category_id = fields.Many2one(
        related='product_id.categ_id', string="Category", readonly=True, store=True)
    quantity = fields.Integer(string='Quantity', default=1, states={
                              'draft': [('readonly', False)]})
    cost = fields.Float(string='Cost', )
    markup = fields.Float(string='MarkUp', default=1.0)
    cost_total = fields.Integer(
        string='Cost Total', compute='_compute_price', readonly=True)
    price_unit = fields.Integer(
        string='Unit Price', compute='_compute_price', readonly=True)
    price_total = fields.Integer(
        string='Total Price', compute='_compute_price', readonly=True)
    company_id = fields.Many2one('res.company', string='Company',
                                 default=lambda self: self.env['res.company']._company_default_get('sale.viatic'), readonly=True, related_sudo=False)
    partner_id = fields.Many2one(
        related='sale_viatic_id.partner_id', string="Partner", readonly=True, store=True)
    user_id = fields.Many2one(
        related='sale_viatic_id.user_id', string="User", readonly=True, store=True)
    state = fields.Selection([('draft', 'Draft'), ('open', 'Open'), (
        'close', 'Close'), ('cancel', 'Cancel')], string='State', default='draft')

    @api.depends('quantity', 'cost', 'markup', 'state')
    def _compute_price(self):
        res = {}
        for line in self:
            cost = line.cost
            price_unit = line.cost * line.markup
            line.cost_total = round(cost * line.quantity, 2)
            line.price_unit = round(price_unit, 2)
            line.price_total = round(price_unit * line.quantity, 2)