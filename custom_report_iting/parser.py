# -*- encoding: utf-8 -*-
################################################################################
#
#  This file is part of Aeroo Reports software - for license refer LICENSE file  
#
################################################################################

# from odoo import api, models



# class ReportAerooAbstract(models.AbstractModel):

# 	_inherit = 'report.report_aeroo.abstract'
# 	_name = 'report.report_aeroo.abstract'
# 	def _get_invoice_name_from_so(self):
# 		print (self)
# 		print (self)
# 		print (self)
# 		invoices = self.mapped('invoice_ids') 
# 		if self.invoice_status == 'invoiced' and len(self.invoices.ids) == 1:
# 			return self.invoices.ids[1].display_name


# 	def complex_report(self, docids, data, report, ctx):
# 		data['context'].update({'get_invoice_name_from_so': self._get_invoice_name_from_so })
# 		ctx.update({'get_invoice_name_from_so': self._get_invoice_name_from_so })
# 		print (data)
# 		print (data)
# 		print (data)
# 		print (data)
# 		return super(ReportAerooAbstract, self).complex_report(docids, data, report, ctx)



from odoo import api, models


class Parser(models.AbstractModel):
	_inherit = 'report.report_aeroo.abstract'

	_name = 'report.iting_report'

	def _get_invoice_name_from_so(self, o):
		invoices = o.mapped('invoice_ids') 
		if o.invoice_status == 'invoiced' and len(invoices) == 1:
			return invoices.display_name

	@api.model
	def aeroo_report(self, docids, data):
		self = self.with_context(get_invoice_name_from_so=self._get_invoice_name_from_so)
		return super(Parser, self).aeroo_report(docids, data)