import time

from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError

class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"


    @api.multi
    def create_invoices(self):
        super(SaleAdvancePaymentInv,self).create_invoices()
        sale_orders = self.env['sale.order'].browse(self._context.get('active_ids', []))
        for sale in sale_orders:
            for invoice in sale.invoice_ids:
                invoice.salesman_id=sale.salesman_id.id
                invoice.user_id=sale.user_id.id
                legend_id = self.env['default.legend.document.company'].search([('company', '=', sale.company_id.id),
                                                                            ('document_type', '=', invoice.journal_document_type_id.document_type_id.id)])
                if legend_id:
                    invoice.legend_in_document = legend_id.default_legend