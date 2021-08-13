##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################


from odoo import api, models, _

class Parser(models.AbstractModel):
    _inherit = 'report.report_aeroo.abstract'
    _name = 'report.account_invoice'
    
    def _get_centro_costo(self,o):
        list_account = {}   
        for line_obj in o.invoice_line_ids:
            if not str(line_obj.account_id.id) in list_account:
                list_account[str(line_obj.account_id.id)] = line_obj.account_id
        var_return = _('')             
        for obj in list_account:
            var_return += _(list_account[obj].name) + _(', ')
        if var_return != _(''):
            var_return = var_return[:-2]
        return var_return

    @api.model
    def aeroo_report(self, docids, data):
        self = self.with_context(get_centro_costo=self._get_centro_costo)
        return super(Parser, self).aeroo_report(docids, data)
