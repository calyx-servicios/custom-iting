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


class SaleOrder(models.Model):
	_inherit = "sale.order"

	salesman_id = fields.Many2one('res.users', string='Salesperson', track_visibility='onchange',
	readonly=True, states={'draft': [('readonly', False)]},
	default=lambda self: self.env.user)

	@api.multi
	def _action_confirm(self):
			ret = super(SaleOrder, self)._action_confirm()
			_logger.info('================iting custom _action_confirm=====')
			for purchase in self.purchase_ids:
				purchase.salesman_id=self.salesman_id.id
			return ret
	
	pre_sale = fields.Many2many(
		string = "Pre-Sale",
		comodel_name = "hr.employee",
		required = True
	)