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
        if vals.get('quantity', 0)<=0:
            raise ValidationError(_('Quantity Must be Positive'))
        return super(SaleViaticLine, self).create(vals)
    
    @api.model
    def write(self, vals):
        if vals.get('quantity') and vals.get('quantity')<=0:
            raise ValidationError(_('Quantity Must be Positive'))
        return super(SaleViaticLine, self).write(vals)

   

    sale_viatic_id = fields.Many2one('sale.viatic', string='Sale Viatic',ondelete='cascade')
    product_id = fields.Many2one('product.product', string='Product', domain=[('viatic_ok', '=', True)], change_default=True, ondelete='restrict', required=True,states={'draft': [('readonly', False)]})
    quantity = fields.Integer(string='Quantity',default=1,states={'draft': [('readonly', False)]})
    cost = fields.Float(string='Cost', )
    markup = fields.Float(string='MarkUp',default=1.0)
    cost_total = fields.Integer(string='Cost Total',compute='_compute_price', readonly=True)
    price_unit = fields.Integer(string='Unit Price',compute='_compute_price',readonly=True)
    price_total = fields.Integer(string='Total Price',compute='_compute_price',readonly=True)
    company_id = fields.Many2one('res.company', string='Company',  
        default=lambda self: self.env['res.company']._company_default_get('sale.viatic'), readonly=True, related_sudo=False)
    partner_id = fields.Many2one(related='sale_viatic_id.partner_id', string="Partner", readonly=True, store=True)
    user_id = fields.Many2one(related='sale_viatic_id.user_id', string="User", readonly=True, store=True)
    state = fields.Selection([('draft', 'Draft'),('open', 'Open'),('close', 'Close'),('cancel', 'Cancel')], string='State',default='draft')

    @api.depends('quantity','cost','markup','state')
    def _compute_price(self):
        res = {}
        for line in self:
            cost=line.cost
            price_unit=line.cost*line.markup
            line.cost_total = round(cost*line.quantity,2)
            line.price_unit = round(price_unit,2)
            line.price_total = round(price_unit*line.quantity,2)


class SaleViatic(models.Model):
    _name = 'sale.viatic'
    _description = 'Sales Viatic'
    _inherit = ['mail.thread']

    @api.model
    def _default_partner(self):
        active_id=self._context.get('active_id')
        if active_id:
            return self.env['sale.order'].browse(active_id).partner_id.id

    @api.model
    def _default_sale(self):
        active_id=self._context.get('active_id')
        return active_id

    @api.model
    def _get_default_viatic_fee(self):
        ICPSudo = self.env['ir.config_parameter'].sudo()
        viatic_fee=float(ICPSudo.get_param('sale_viatic.viatic_fee') or 0.0)
        return viatic_fee

    @api.model
    def _get_default_viatic_tax(self):
        ICPSudo = self.env['ir.config_parameter'].sudo()
        viatic_tax=float(ICPSudo.get_param('sale_viatic.viatic_tax') or 0.0)
        return viatic_tax

        

    @api.model
    def _default_lines(self):
        product_obj = self.env['product.product']
        lines = []
        for product in product_obj.search([('viatic_ok','=',True)]):
                    lines.append({'product_id':product.id,
                        'quantity':0,
                        })
        return lines

    name = fields.Char(string='Order Reference', required=True, copy=False, readonly=True, states={'draft': [('readonly', False)]}, index=True, default=lambda self: _('New'))

    sale_order_id = fields.Many2one('sale.order', string='Sale Order', default=_default_sale,required=True,ondelete='cascade')
    date_viatic = fields.Datetime(string='Date', required=True, readonly=True, index=True, states={'draft': [('readonly', False)]}, default=fields.Datetime.now)
    partner_id = fields.Many2one(related='sale_order_id.partner_id', string="Partner", readonly=True, store=True)
    line_ids = fields.One2many('sale.viatic.line', 'sale_viatic_id', string='Viatic Lines',states={'draft': [('readonly', False)]},default=_default_lines)
    user_id = fields.Many2one('res.users',  string="User Create", states={'draft': [('readonly', False)]},
        default=lambda self: self.env.user)
    company_id = fields.Many2one('res.company', string='Company',  
        default=lambda self: self.env['res.company']._company_default_get('sale.viatic'), readonly=True, related_sudo=False)
    state = fields.Selection([('draft', 'Draft'),('open', 'Open'),('close', 'Close'),('cancel', 'Cancel')], string='State',default='draft')
    note = fields.Text('Terms and conditions',)
    manual_rate = fields.Float('Manual Rate',)
    cost_total = fields.Float('Total Cost',compute='_compute_total',readonly=True)
    cost_usd_total = fields.Float('Total USD Cost',compute='_compute_total',readonly=True)
    price_total = fields.Float('Total',compute='_compute_total',readonly=True)
    price_usd_total = fields.Float('Total USD',compute='_compute_total',readonly=True)
    pricelist_id = fields.Many2one(related='sale_order_id.pricelist_id', string='Pricelist', readonly=True)
    currency_id = fields.Many2one(related='sale_order_id.currency_id', string="Currency", readonly=True)
    sale_total = fields.Monetary(related='sale_order_id.amount_untaxed', string="Sale Amount", readonly=True, store=True)
    net_profit= fields.Float('Net Profit',compute='_compute_profit',readonly=True)
    gross_profit= fields.Float('Gross Profit',compute='_compute_profit',readonly=True)
    fee_amount= fields.Float('Fee',compute='_compute_profit',readonly=True)
    tax_amount= fields.Float('Tax',compute='_compute_profit',readonly=True)
    net_contribution= fields.Float('Net Contribution',compute='_compute_profit',readonly=True)
    viatic_fee= fields.Float('Viatic Fee',default=_get_default_viatic_fee)
    viatic_tax= fields.Float('Viatic Tax',default=_get_default_viatic_tax)

    @api.depends('sale_order_id.amount_untaxed','sale_order_id','line_ids','viatic_tax','viatic_fee','state','manual_rate','line_ids.quantity','line_ids.markup','line_ids.cost')
    def _compute_profit(self):
        for viatic in self:
            gross_profit=0.0
            net_profit=0.0
            tax_amount=0.0
            fee_amount=0.0
            net_contribution=0.0
            if viatic.sale_order_id:
                untaxed_amount=viatic.sale_order_id.amount_untaxed
                gross_profit=untaxed_amount-viatic.cost_total
                fee_amount=untaxed_amount*viatic.viatic_fee/100.0
                tax_amount=untaxed_amount*viatic.viatic_tax/100.0
                net_profit=gross_profit-fee_amount-tax_amount
                if untaxed_amount!=0:
                    net_contribution=net_profit/untaxed_amount
            viatic.gross_profit=round(gross_profit,2)
            viatic.net_profit=round(net_profit,2)
            viatic.tax_amount=round(tax_amount,2)
            viatic.fee_amount=round(fee_amount,2)
            viatic.net_contribution=round(net_contribution,2)

    @api.depends('line_ids','state','manual_rate','line_ids.quantity','line_ids.markup','line_ids.cost')
    def _compute_total(self):
        res = {}
        for viatic in self:
            cost_total=0.0
            price_total=0.0
            cost_usd_total=0.0
            price_usd_total=0.0
            for line in viatic.line_ids:
                cost_total+=line.cost*line.quantity
                price_total+=line.cost*line.markup*line.quantity
            if viatic.manual_rate and viatic.manual_rate>0:
                    cost_usd_total=cost_total/viatic.manual_rate
                    price_usd_total=price_total/viatic.manual_rate
            viatic.cost_total=round(cost_total,2)
            viatic.cost_usd_total=round(cost_usd_total,2)
            viatic.price_total=round(price_total,2)
            viatic.price_usd_total=round(price_usd_total,2)


    @api.multi
    def unlink(self):
        for viatic in self:
            if viatic.state not in ('draft', 'cancel'):
                raise UserError(_('You cannot delete a viatic which is not draft or cancelled. You should cancel it first.'))
        return super(SaleViatic, self).unlink()
                    

    @api.model
    def create(self, vals):
        if vals.get('sale_order_id') and not vals.get('partner_id'):
            sale = self.env['sale.order'].browse(vals.get('sale_order_id'))
            vals['partner_id']=sale.partner_id.id
        if vals.get('name', _('New')) == _('New'):
            if 'company_id' in vals:
                vals['name'] = self.env['ir.sequence'].with_context(force_company=vals['company_id']).next_by_code('sale.viatic') or _('New')
            else:
                vals['name'] = self.env['ir.sequence'].next_by_code('sale.viatic') or _('New')
        return super(SaleViatic, self).create(vals)




    @api.multi
    def action_draft(self):
        orders = self.filtered(lambda s: s.state in ['cancel'])
        return orders.write({
            'state': 'draft',
        })

    

    @api.multi
    def action_set(self):
        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        ICPSudo = self.env['ir.config_parameter'].sudo()
        line_obj=self.env['sale.order.line']
        viatic_product_id = literal_eval(ICPSudo.get_param('sale_viatic.viatic_product', default='False'))
        if viatic_product_id and not self.env['product.product'].browse(viatic_product_id).exists():
            viatic_product_id = False
            raise UserError(_('The default Viatic product is not defined. Please review the Viatic settings'))
        
        if viatic_product_id:
            for viatic in self:
                if viatic.pricelist_id and viatic.pricelist_id.currency_id.id!=viatic.company_id.currency_id.id and viatic.manual_rate<=0:
                    raise UserError(_('You must set a manual rate for currency or set the default company currency on the sale order'))
                total=viatic.price_total
                if viatic.pricelist_id.currency_id.id!=viatic.company_id.currency_id.id:
                    total=viatic.price_usd_total
                line_id=line_obj.search([('order_id','=',viatic.sale_order_id.id),('product_id','=',viatic_product_id)])
                if line_id:
                    line_id.price_unit=total
                    line_id.product_uom_qty=1.0
                else:
                    line_obj.create({
                        'order_id':self.sale_order_id.id,
                        'product_id':viatic_product_id,
                        'product_uom_qty': 1.0,
                        'price_unit':total
                    })
                compose_form_id = ir_model_data.get_object_reference('sale', 'view_order_form')[1]
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
    
