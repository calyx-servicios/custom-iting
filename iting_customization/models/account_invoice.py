##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta
import requests
import sys
from lxml import html
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning

import re
import logging
_logger = logging.getLogger(__name__)


class AccountInvoice(models.Model):
    _inherit = "account.invoice"
    

    @api.model
    def _default_user(self):
        if self._context.get('active_model') == 'purchase.order' and self._context.get('active_ids'):
            order = self.env['purchase.order'].browse(self._context['active_ids'])[0]
            return order.user_id.id
        else:
            return self.env.user
    
    @api.model
    def _default_salesman(self):
        if self._context.get('active_model') == 'purchase.order' and self._context.get('active_ids'):
            order = self.env['purchase.order'].browse(self._context['active_ids'])[0]
            return order.salesman_id.id
        else:
            return self.env.user

    user_id = fields.Many2one('res.users', string='Salesperson', track_visibility='onchange',
        readonly=True, states={'draft': [('readonly', False)]},
        default=_default_user, required=True)

    salesman_id = fields.Many2one('res.users', string='Salesman', track_visibility='onchange',
        readonly=True, states={'draft': [('readonly', False)]},
        default=_default_salesman)

    @api.onchange('currency_id')
    def reset_rate(self):
        self.currency_rate = 0.0
        return {
                'currency_rate': self.currency_rate
            }


    @api.multi
    def action_invoice_open(self):
        to_open_invoices = self.filtered(lambda inv: inv.state != 'open')
        currency_id=self.env.user.company_id.currency_id.id
        for invoice in to_open_invoices:

            if invoice.currency_id and invoice.currency_id.id!=currency_id:
                if invoice.currency_rate==0.0:
                    raise ValidationError(_('Currency Rate must be defined '))

        super(AccountInvoice, self).action_invoice_open()




