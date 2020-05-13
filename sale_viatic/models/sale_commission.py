from odoo import models, api, fields, _
from ast import literal_eval
import logging
from odoo.exceptions import ValidationError, UserError
_logger = logging.getLogger(__name__)


class SaleCommission(models.Model):
    _name = 'sale.commission'
    _description = 'Sales Commission'
    _inherit = ['mail.thread']
    _order = 'id desc'

    @api.model
    def _default_sale(self):
        active_id = self._context.get('active_id')
        return active_id

    sale_order_id = fields.Many2one(
        'sale.order', string='Sale Order', default=_default_sale, required=True, ondelete='cascade')
    net_profit = fields.Float(
        'Net Profit', related='sale_order_id.net_profit', readonly=True)
    commission_state = fields.Selection(
        [('draft', 'Draft'), ('paid', 'Paid'), ('cancel', 'Cancel')], string='State', default='draft')
    commission_amount = fields.Float(
        'Comission Amount', compute='_compute_commission', store=True, readonly=True)
    commission_percentage = fields.Float('Commission Percentage', states={
                                         'draft': [('readonly', False)]})
    salesman_id = fields.Many2one(
        related='sale_order_id.user_id', store=True, string='Salesperson', readonly=True)

    @api.depends('commission_percentage', 'sale_order_id.net_profit')
    def _compute_commission(self):
        res = {}
        for line in self:
            line.commission_amount = round(
                line.commission_percentage * self.sale_order_id.net_profit / 100.0, 2)
