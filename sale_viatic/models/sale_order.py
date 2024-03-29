# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, api, fields, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import ValidationError
from ast import literal_eval
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning

class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.model
    def _get_default_viatic_fee(self):
        ICPSudo = self.env['ir.config_parameter'].sudo()
        viatic_fee = float(ICPSudo.get_param('sale_viatic.viatic_fee') or 0.0)
        return viatic_fee

    @api.model
    def _get_default_viatic_tax(self):
        ICPSudo = self.env['ir.config_parameter'].sudo()
        viatic_tax = float(ICPSudo.get_param('sale_viatic.viatic_tax') or 0.0)
        return viatic_tax

    viatic_ids = fields.One2many(
        'sale.viatic', 'sale_order_id', string='Viatic Lines')
    commission_ids = fields.One2many(
        'sale.commission', 'sale_order_id', string='Commission Lines')
    amount_cost = fields.Monetary(compute='_sale_cost', help="It gives total cost.",
                                  currency_field='currency_id', digits=dp.get_precision('Product Price'), store=True)

    net_profit = fields.Float(
        'Net Profit', compute='_compute_profit', readonly=True, store=True)
    gross_profit = fields.Float(
        'Gross Profit', compute='_compute_profit', readonly=True, store=True)
    fee_amount = fields.Float(
        'Fee', compute='_compute_profit', readonly=True, store=True)
    tax_amount = fields.Float(
        'Tax', compute='_compute_profit', readonly=True, store=True)
    net_contribution = fields.Float(
        'Net Contribution', compute='_compute_profit', readonly=True, store=True)
    viatic_fee = fields.Float('Viatic Fee', default=_get_default_viatic_fee, states={
                              'draft': [('readonly', False)]})
    viatic_tax = fields.Float('Viatic Tax', default=_get_default_viatic_tax, states={
                              'draft': [('readonly', False)]})
    invoice_names = fields.Char(
        'Invoice Names', compute='_compute_names', store=True, readonly=True)
    invoice_state = fields.Selection(
        [('paid', 'Paid'), ('open', 'Open')], compute='_compute_names', store=True, readonly=True)

    #@api.depends('invoice_ids', 'invoice_ids.state')
    def _compute_names(self):
        for order in self:
            for viatic in order.viatic_ids:
                names = ''
                paid = False
                for invoice in viatic.invoice_ids:
                    if invoice.state in ['paid']:
                        paid = True
                    if invoice.state in ['open', 'paid']:
                        names += invoice.display_name + '|'
                if paid:
                    viatic.invoice_state = 'paid'
                else:
                    viatic.invoice_state = 'open'
                viatic.invoice_names = names

    @api.depends('amount_untaxed', 'viatic_tax', 'viatic_fee', 'state', 'viatic_ids', 'order_line', 'amount_cost')
    def _compute_profit(self):
        for viatic in self:
            gross_profit = 0.0
            net_profit = 0.0
            tax_amount = 0.0
            fee_amount = 0.0
            net_contribution = 0.0
            if viatic:
                untaxed_amount = viatic.amount_untaxed - \
                    viatic.amount_cost
                gross_profit = untaxed_amount
                #
                # gross_profit=untaxed_amount-viatic.cost_total
                fee_amount = viatic.amount_untaxed * viatic.viatic_fee / 100.0
                tax_amount = viatic.amount_untaxed * viatic.viatic_tax / 100.0
                net_profit = gross_profit - fee_amount - tax_amount
                if viatic.amount_untaxed != 0:
                    net_contribution = (
                        net_profit / viatic.amount_untaxed) * 100
            viatic.gross_profit = round(gross_profit, 2)
            viatic.net_profit = round(net_profit, 2)
            viatic.tax_amount = round(tax_amount, 2)
            viatic.fee_amount = round(fee_amount, 2)
            viatic.net_contribution = round(net_contribution, 2)

    @api.depends('order_line.cost', 'order_line.product_id', 'order_line.purchase_price', 'order_line.product_uom_qty', 'order_line')
    def _sale_cost(self):
        for order in self:
            order.amount_cost = sum(order.order_line.filtered(
                lambda r: r.state != 'cancel').mapped('cost'))

    # def set_viatics(self):
    #     return {
    #         'name': _("Viatics"),
    #         'type': 'ir.actions.act_window',
    #         'view_type': 'form',
    #         'view_mode': 'form',
    #         'res_model': 'sale.viatic.wizard',
    #         'target': 'new',

    #     }

    def set_viatics(self):
        ICPSudo = self.env['ir.config_parameter'].sudo()
        line_obj = self.env['sale.order.line']
        viatic_product_id = literal_eval(ICPSudo.get_param(
            'sale_viatic.viatic_product', default='False'))
        if viatic_product_id and not self.env['product.product'].browse(viatic_product_id).exists():
            viatic_product_id = False
            raise UserError(
                _('The default Viatic product is not defined. Please review the Viatic settings'))
        if self.state not in ['draft']:
            raise UserError(_('The sale order must be in draft state'))
        else:
            for viatic in self.viatic_ids:
                if viatic.state not in ['draft']:
                    raise UserError(_('The viatic must be in draft state'))
                if viatic.sale_order_id.pricelist_id and viatic.sale_order_id.pricelist_id.currency_id.id != viatic.company_id.currency_id.id and viatic.manual_rate <= 0:
                    raise UserError(
                        _('You must set a manual rate for currency or set the default company currency on the sale order'))
                total = viatic.price_total
                cost_total = viatic.cost_total
                if viatic.sale_order_id.pricelist_id.currency_id.id != viatic.company_id.currency_id.id:
                    total = viatic.price_usd_total
                    cost_total = viatic.cost_usd_total
                line_id = line_obj.search(
                    [('order_id', '=', viatic.sale_order_id.id), ('product_id', '=', viatic_product_id)])
                if line_id:
                    line_id.price_unit = total
                    line_id.product_uom_qty = 1.0
                    line_id.purchase_price = cost_total
                else:
                    line_obj.create({
                        'order_id': self.id,
                        'product_id': viatic_product_id,
                        'product_uom_qty': 1.0,
                        'price_unit': total,
                        'purchase_price': cost_total,
                    })
                viatic.action_open()

    @api.multi
    def set_commisions(self):
        if len(self.commission_ids) == 0:
            vals = {
                'sale_order_id': self.id,
                'commission_state': 'draft',
            }
            self.env['sale.commission'].create(vals)

    @api.multi
    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        self.confirm_viatics()
        self.set_commisions()
        return res

    @api.multi
    def confirm_viatics(self):
        for order in self:
            for viatic in order.viatic_ids:
                if viatic.state == 'draft':
                    viatic.action_open()

    @api.multi
    def action_cancel(self):
        res = super(SaleOrder, self).action_cancel()
        return res

    @api.multi
    def cancel_viatics(self):
        for order in self:
            for viatic in order.viatic_ids:
                if viatic.state == 'open':
                    viatic.action_cancel()


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    cost = fields.Float(compute='_product_cost',
                        digits=dp.get_precision('Product Price'), store=True)

    @api.depends('product_id', 'purchase_price', 'product_uom_qty')
    def _product_cost(self):
        for line in self:
            #currency = line.order_id.pricelist_id.currency_id
            price = line.purchase_price
            line.cost = price * line.product_uom_qty

    @api.model
    def create(self, vals):
        purchase_price = vals.get("purchase_price")
        if purchase_price==0.00:
            raise ValidationError("Cost price field cannot be 0")
        return super(SaleOrderLine, self).create(vals)