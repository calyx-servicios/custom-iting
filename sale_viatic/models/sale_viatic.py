from odoo import models, api, fields, _
from ast import literal_eval
import logging
from odoo.exceptions import ValidationError, UserError
_logger = logging.getLogger(__name__)


class SaleViatic(models.Model):
    _name = 'sale.viatic'
    _description = 'Sales Viatic'
    _inherit = ['mail.thread']
    _order = 'id desc'

    @api.model
    def _default_partner(self):
        active_id = self._context.get('active_id')
        if active_id:
            return self.env['sale.order'].browse(active_id).partner_id.id

    @api.model
    def _default_sale(self):
        active_id = self._context.get('active_id')
        return active_id



    @api.model
    def _default_lines(self):
        product_obj = self.env['product.product']
        lines = []
        for product in product_obj.search([('viatic_ok', '=', True)]):
            lines.append({'product_id': product.id,
                          'quantity': 0,
                          })
        return lines

    name = fields.Char(string='Order Reference', required=True, copy=False, readonly=True, states={
                       'draft': [('readonly', False)]}, index=True, default=lambda self: _('New'))

    sale_order_id = fields.Many2one(
        'sale.order', string='Sale Order', default=_default_sale, required=True, ondelete='cascade')
    date_viatic = fields.Datetime(string='Date', required=True, readonly=True, index=True, states={
                                  'draft': [('readonly', False)]}, default=fields.Datetime.now)
    partner_id = fields.Many2one(
        related='sale_order_id.partner_id', string="Partner", readonly=True, store=True)
    line_ids = fields.One2many('sale.viatic.line', 'sale_viatic_id', string='Viatic Lines', states={
                               'draft': [('readonly', False)]}, default=_default_lines)
    user_id = fields.Many2one('res.users',  string="User Create", states={'draft': [('readonly', False)]},
                              default=lambda self: self.env.user)
    company_id = fields.Many2one('res.company', string='Company',
                                 default=lambda self: self.env['res.company']._company_default_get('sale.viatic'), readonly=True, related_sudo=False)
    state = fields.Selection([('draft', 'Draft'), ('open', 'Open'), (
        'close', 'Close'), ('cancel', 'Cancel')], string='State', default='draft')
    note = fields.Text('Terms and conditions', states={
                       'draft': [('readonly', False)]})
    manual_rate = fields.Float('Manual Rate', states={
                               'draft': [('readonly', False)]})
    #esto queda aca
    cost_total = fields.Float(
        'Total Cost', compute='_compute_total', readonly=True, store=True)
    cost_usd_total = fields.Float(
        'Total USD Cost', compute='_compute_total', readonly=True, store=True)
    price_total = fields.Float(
        'Total', compute='_compute_total', readonly=True, store=True)
    price_usd_total = fields.Float(
        'Total USD', compute='_compute_total', readonly=True, store=True)

    #esto no se
    invoice_ids = fields.Many2many(
        related='sale_order_id.invoice_ids', string='Invoices')


    #se queda
    @api.depends('line_ids', 'state', 'manual_rate', 'line_ids.quantity', 'line_ids.markup', 'line_ids.cost')
    def _compute_total(self):
        res = {}
        for viatic in self:
            cost_total = 0.0
            price_total = 0.0
            cost_usd_total = 0.0
            price_usd_total = 0.0
            for line in viatic.line_ids:
                cost_total += line.cost * line.quantity
                price_total += line.cost * line.markup * line.quantity
            if viatic.manual_rate and viatic.manual_rate > 0:
                cost_usd_total = cost_total / viatic.manual_rate
                price_usd_total = price_total / viatic.manual_rate
            viatic.cost_total = round(cost_total, 2)
            viatic.cost_usd_total = round(cost_usd_total, 2)
            viatic.price_total = round(price_total, 2)
            viatic.price_usd_total = round(price_usd_total, 2)

    @api.multi
    def unlink(self):
        for viatic in self:
            if viatic.state not in ('draft', 'cancel'):
                raise UserError(
                    _('You cannot delete a viatic which is not draft or cancelled. You should cancel it first.'))
        return super(SaleViatic, self).unlink()

    @api.model
    def create(self, vals):
        if vals.get('sale_order_id') and not vals.get('partner_id'):
            sale = self.env['sale.order'].browse(vals.get('sale_order_id'))
            vals['partner_id'] = sale.partner_id.id
        if vals.get('name', _('New')) == _('New'):
            if 'company_id' in vals:
                vals['name'] = self.env['ir.sequence'].with_context(
                    force_company=vals['company_id']).next_by_code('sale.viatic') or _('New')
            else:
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'sale.viatic') or _('New')
        return super(SaleViatic, self).create(vals)

    @api.multi
    def action_draft(self):
        viatics = self.filtered(lambda s: s.state in ['cancel'])
        return viatics.write({
            'state': 'draft',
        })

    @api.multi
    def action_close(self):
        viatics = self.filtered(lambda s: s.state in ['open'])
        return viatics.write({
            'state': 'close',
        })

    @api.multi
    def action_cancel(self):
        viatics = self.filtered(lambda s: s.state in ['open', 'draft'])
        return viatics.write({
            'state': 'cancel',
        })

    @api.multi
    def action_open(self):
        viatics = self.filtered(lambda s: s.state in ['draft'])
        return viatics.write({
            'state': 'open',
        })

    @api.multi
    def action_set(self):
        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        ICPSudo = self.env['ir.config_parameter'].sudo()
        line_obj = self.env['sale.order.line']
        viatic_product_id = literal_eval(ICPSudo.get_param(
            'sale_viatic.viatic_product', default='False'))
        if viatic_product_id and not self.env['product.product'].browse(viatic_product_id).exists():
            viatic_product_id = False
            raise UserError(
                _('The default Viatic product is not defined. Please review the Viatic settings'))
        if self.sale_order_id and self.sale_order_id.state not in ['draft']:
            raise UserError(_('The sale order must be in draft state'))

        if viatic_product_id:
            for viatic in self:
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
                        'order_id': self.sale_order_id.id,
                        'product_id': viatic_product_id,
                        'product_uom_qty': 1.0,
                        'price_unit': total,
                        'purchase_price': cost_total,
                    })
                compose_form_id = ir_model_data.get_object_reference(
                    'sale', 'view_order_form')[1]
                return {
                    'name': _('Sale Order'),
                    'type': 'ir.actions.act_window',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'sale.order',
                    'res_id': self.sale_order_id.id,
                    'views': [(compose_form_id, 'form')],
                    'view_id': compose_form_id,
                    'context': {},
                }
